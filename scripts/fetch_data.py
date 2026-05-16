"""Fetch public VC / unicorn datasets into data/raw/.

This script pulls **only public data**. It does not access any restricted
or proprietary source. Run from the repo root:

    python scripts/fetch_data.py

Outputs:
    data/raw/unicorns_YYYY-MM-DD.csv   # timestamped snapshot
    data/raw/unicorns.csv              # stable copy that notebooks load
    data/raw/_fetch_log.json           # provenance log

Sources tried, in order:
    1. CB Insights unicorn research page (HTML scrape — no API key required).
    2. Wikipedia "List of unicorn startup companies" (stable mirror, fallback).

If both fail (e.g. no network), the script exits non-zero and the notebooks
will print a clear message telling the user to re-run this script.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = (
    "vc-pattern-notebooks/0.1 (+https://github.com/mkzung/vc-pattern-notebooks) "
    "research-public-data-only"
)

CBI_URL = "https://www.cbinsights.com/research-unicorn-companies"
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies"

# CB Insights does NOT publish founded_year. Wikipedia's list does, so we
# pull Wikipedia separately and left-merge by company name to enrich the
# CB Insights table with a best-effort founding year.


def _http_get(url: str, timeout: int = 30) -> str | None:
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as exc:  # noqa: BLE001
        print(f"  ! GET {url} failed: {exc}", file=sys.stderr)
        return None


def fetch_cbinsights() -> pd.DataFrame | None:
    """Try to parse CB Insights' public unicorn table.

    CB Insights periodically changes their markup. We look for the first
    <table> on the page and require columns that look like a unicorn list.
    """
    print(f"[1/2] CB Insights: {CBI_URL}")
    html = _http_get(CBI_URL)
    if html is None:
        return None
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    for tbl in tables:
        try:
            df = pd.read_html(str(tbl))[0]
        except ValueError:
            continue
        cols_lower = [str(c).lower() for c in df.columns]
        if any("compan" in c for c in cols_lower) and any(
            "valuat" in c for c in cols_lower
        ):
            df.columns = [str(c).strip() for c in df.columns]
            return df
    print("  ! CB Insights: no recognizable unicorn table on page", file=sys.stderr)
    return None


def fetch_wikipedia() -> pd.DataFrame | None:
    """Fallback: Wikipedia's list of unicorn startup companies."""
    print(f"[2/2] Wikipedia fallback: {WIKI_URL}")
    html = _http_get(WIKI_URL)
    if html is None:
        return None
    try:
        tables = pd.read_html(html)
    except ValueError:
        return None
    # Pick the largest table that has a "Company" or "Valuation" column.
    candidates = []
    for t in tables:
        cols_lower = [str(c).lower() for c in t.columns]
        if any("compan" in c for c in cols_lower) and any(
            "valuat" in c or "country" in c or "industry" in c for c in cols_lower
        ):
            candidates.append(t)
    if not candidates:
        print("  ! Wikipedia: no unicorn-shaped table found", file=sys.stderr)
        return None
    df = max(candidates, key=len)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Light normalization so downstream notebooks have stable column names."""
    rename = {}
    for c in df.columns:
        cl = c.lower()
        if "compan" in cl and "company" not in rename.values():
            rename[c] = "company"
        elif "valuat" in cl and "valuation_usd_b" not in rename.values():
            rename[c] = "valuation_usd_b"
        elif "country" in cl or "location" in cl or "headquart" in cl:
            rename[c] = "country"
        elif "industr" in cl or "sector" in cl or "category" in cl:
            rename[c] = "sector"
        elif "founded" in cl or "founding" in cl:
            rename[c] = "founded_year"
        elif "joined" in cl or "date joined" in cl or "unicorn" in cl:
            rename[c] = "unicorn_year"
        elif "investor" in cl:
            rename[c] = "select_investors"
    out = df.rename(columns=rename).copy()
    # Best-effort year extraction
    for col in ("founded_year", "unicorn_year"):
        if col in out.columns:
            out[col] = (
                out[col]
                .astype(str)
                .str.extract(r"(\d{4})", expand=False)
                .astype("Int64")
            )
    return out


def fetch_wikipedia_founders() -> pd.DataFrame | None:
    """Pull Wikipedia's current-unicorn table for its `Founder(s)` column.

    Returns a long-form DataFrame: one row per (company, founder_name).
    Used by Notebook 03 as a public founders file.
    """
    print(f"[+] Wikipedia founders: {WIKI_URL}")
    html = _http_get(WIKI_URL)
    if html is None:
        return None
    try:
        tables = pd.read_html(html)
    except ValueError:
        return None
    candidate = None
    for t in tables:
        cols_lower = [str(c).lower() for c in t.columns]
        if (
            any("founder" in c for c in cols_lower)
            and any("compan" in c for c in cols_lower)
            and (candidate is None or len(t) > len(candidate))
        ):
            candidate = t
    if candidate is None:
        return None
    candidate = candidate.copy()
    candidate.columns = [str(c).strip() for c in candidate.columns]
    company_col = next((c for c in candidate.columns if "compan" in c.lower()), None)
    founder_col = next((c for c in candidate.columns if "founder" in c.lower()), None)
    if not (company_col and founder_col):
        return None
    rows = []
    for _, r in candidate[[company_col, founder_col]].dropna().iterrows():
        company = str(r[company_col]).strip()
        raw = str(r[founder_col])
        # Split on common delimiters that appear in Wikipedia founder cells.
        parts = re.split(r",| and |;|/|·", raw)
        for p in parts:
            name = p.strip()
            if name and not name.lower().startswith("see "):
                rows.append({"company": company, "founder_name": name})
    if not rows:
        return None
    return pd.DataFrame(rows)


def main() -> int:
    today = date.today().isoformat()
    df = fetch_cbinsights()
    source = "cbinsights"
    if df is None or len(df) < 50:
        df = fetch_wikipedia()
        source = "wikipedia"
    if df is None or df.empty:
        print(
            "ERROR: could not fetch a public unicorn list from either source.\n"
            "Check network connectivity and re-run.",
            file=sys.stderr,
        )
        return 1

    df = normalize(df)

    # Also pull Wikipedia founders into a separate long-form file used by
    # Notebook 03. This is best-effort: Wikipedia's coverage is uneven and
    # we make no attempt here to disambiguate founder identities.
    founders = fetch_wikipedia_founders()
    if founders is not None and not founders.empty:
        fnd_path = RAW_DIR / "founders.csv"
        founders.to_csv(fnd_path, index=False)
        print(f"  + wrote {len(founders):,} founder rows -> {fnd_path.relative_to(REPO_ROOT)}")
    snap = RAW_DIR / f"unicorns_{today}.csv"
    stable = RAW_DIR / "unicorns.csv"
    df.to_csv(snap, index=False)
    shutil.copyfile(snap, stable)

    log_path = RAW_DIR / "_fetch_log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else []
    log.append(
        {
            "date": today,
            "source": source,
            "url": CBI_URL if source == "cbinsights" else WIKI_URL,
            "rows": int(len(df)),
            "snapshot": snap.name,
        }
    )
    log_path.write_text(json.dumps(log, indent=2))

    print(
        f"\nOK: wrote {len(df)} rows from {source} -> {snap.relative_to(REPO_ROOT)}\n"
        f"     stable copy -> {stable.relative_to(REPO_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
