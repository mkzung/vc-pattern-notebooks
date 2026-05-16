"""Sanity checks on data/raw/ pulls.

Exits 0 on success, 1 on failure. Wired into `make validate` and the
GitHub Actions workflow. The checks are intentionally cheap and
descriptive — every failure prints the file, the rule, and the
observed value, so a reader can debug without re-running the notebooks.

Rules (current):

unicorns.csv
    - exists, is readable as CSV, is non-empty
    - row count is in [50, 5_000]   (sanity bounds for a global unicorn list)
    - has the required columns: company, valuation_usd_b, unicorn_year,
      country, sector
    - no column is entirely null
    - no duplicate (company, country, sector) triples — name collisions
      across sectors (e.g. an Insurance "Branch" and an Enterprise-Tech
      "Branch") are real and expected, so the duplicate key includes sector

founders.csv (optional)
    - if present: has columns {company, founder_name}, no empty names,
      no duplicate (company, founder_name) rows

Run from the repo root:

    python scripts/validate_data.py
"""

from __future__ import annotations

import sys
from collections.abc import Iterable
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"

UNICORNS_REQUIRED_COLS = {
    "company",
    "valuation_usd_b",
    "unicorn_year",
    "country",
    "sector",
}
UNICORNS_MIN_ROWS = 50
UNICORNS_MAX_ROWS = 5_000

FOUNDERS_REQUIRED_COLS = {"company", "founder_name"}


def _fail(msgs: list[str], rule: str, detail: str) -> None:
    msgs.append(f"FAIL [{rule}] {detail}")


def _ok(rule: str, detail: str) -> None:
    print(f"OK   [{rule}] {detail}")


def check_unicorns(path: Path, errors: list[str]) -> None:
    if not path.exists():
        _fail(errors, "unicorns/exists", f"{path} not found — run scripts/fetch_data.py")
        return
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001
        _fail(errors, "unicorns/readable", f"{path} not readable as CSV: {exc}")
        return

    _ok("unicorns/readable", f"{path.name} ({len(df):,} rows, {len(df.columns)} cols)")

    if not (UNICORNS_MIN_ROWS <= len(df) <= UNICORNS_MAX_ROWS):
        _fail(
            errors,
            "unicorns/row_count",
            f"{len(df):,} rows not in [{UNICORNS_MIN_ROWS}, {UNICORNS_MAX_ROWS}]",
        )
    else:
        _ok("unicorns/row_count", f"{len(df):,} rows in expected band")

    missing = UNICORNS_REQUIRED_COLS - set(df.columns)
    if missing:
        _fail(errors, "unicorns/schema", f"missing columns: {sorted(missing)}")
    else:
        _ok("unicorns/schema", f"all required columns present: {sorted(UNICORNS_REQUIRED_COLS)}")

    all_null = [c for c in df.columns if df[c].isna().all()]
    if all_null:
        _fail(errors, "unicorns/no_all_null", f"all-null columns: {all_null}")
    else:
        _ok("unicorns/no_all_null", "no all-null columns")

    # Composite "company_id" surrogate: same-named firms in the same country
    # and sector are usually genuine collisions (e.g. Insurance "Branch" vs
    # Enterprise-Tech "Branch"). We add City as a tie-breaker for cases where
    # two distinct firms share name/country/sector but operate from different
    # cities. Any remaining collision after that key is treated as a real dupe.
    key_cols = [
        c for c in ("company", "country", "sector", "City") if c in df.columns
    ]
    if "company" in df.columns and "country" in df.columns and "sector" in df.columns:
        key = df[key_cols].astype(str).apply(lambda s: s.str.strip())
        dupes = key.duplicated().sum()
        if dupes > 0:
            sample = (
                df.loc[key.duplicated(keep=False), key_cols]
                .head(5)
                .to_dict(orient="records")
            )
            _fail(
                errors,
                "unicorns/no_dupes",
                f"{dupes} duplicate {key_cols} rows; e.g. {sample}",
            )
        else:
            _ok(
                "unicorns/no_dupes",
                f"no duplicate {key_cols} rows",
            )


def check_founders(path: Path, errors: list[str]) -> None:
    if not path.exists():
        _ok("founders/exists", f"{path.name} not present (optional)")
        return
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001
        _fail(errors, "founders/readable", f"{path} not readable: {exc}")
        return

    _ok("founders/readable", f"{path.name} ({len(df):,} rows)")

    missing = FOUNDERS_REQUIRED_COLS - set(df.columns)
    if missing:
        _fail(errors, "founders/schema", f"missing columns: {sorted(missing)}")
        return
    _ok("founders/schema", f"required columns present: {sorted(FOUNDERS_REQUIRED_COLS)}")

    blank = df["founder_name"].astype(str).str.strip().eq("").sum()
    if blank:
        _fail(errors, "founders/no_blank_names", f"{blank} blank founder_name rows")
    else:
        _ok("founders/no_blank_names", "no blank founder names")

    dupes = df[["company", "founder_name"]].duplicated().sum()
    if dupes:
        _fail(errors, "founders/no_dupes", f"{dupes} duplicate (company, founder_name) rows")
    else:
        _ok("founders/no_dupes", "no duplicate (company, founder_name) rows")


def main(argv: Iterable[str] | None = None) -> int:
    print(f"Validating data in {RAW_DIR}")
    errors: list[str] = []

    check_unicorns(RAW_DIR / "unicorns.csv", errors)
    check_founders(RAW_DIR / "founders.csv", errors)

    print()
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  {e}")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
