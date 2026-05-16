"""Refresh public data with timestamped suffix and diff against the prior pull.

This is the long-running companion to `fetch_data.py`. `fetch_data.py`
overwrites `data/raw/unicorns.csv` so notebooks always read the latest.
`refresh_data.py` is the one you run on a cadence (weekly / monthly):
it pulls a new snapshot, keeps the previous stable copy as
`unicorns_prev.csv`, and logs a diff so a reader can see what changed
between pulls without re-running the notebooks.

Usage:

    python scripts/refresh_data.py
    python scripts/refresh_data.py --dry-run    # show diff, don't write

Diff output is appended to `data/raw/_refresh_log.json` and a human-
readable line is printed to stdout.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"

# Import fetch_data lazily so this script works even if scripts/ isn't a package.
sys.path.insert(0, str(Path(__file__).resolve().parent))


def diff_frames(old: pd.DataFrame, new: pd.DataFrame) -> dict:
    """Coarse diff between two unicorn snapshots, keyed on company."""
    old_cos = set(old["company"].astype(str).str.strip()) if "company" in old else set()
    new_cos = set(new["company"].astype(str).str.strip()) if "company" in new else set()
    added = sorted(new_cos - old_cos)
    dropped = sorted(old_cos - new_cos)
    return {
        "n_old": int(len(old)),
        "n_new": int(len(new)),
        "n_added": len(added),
        "n_dropped": len(dropped),
        "added_sample": added[:10],
        "dropped_sample": dropped[:10],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", help="show diff, do not write files")
    args = p.parse_args()

    import fetch_data  # noqa: WPS433 (local import on purpose)

    stable = RAW_DIR / "unicorns.csv"
    old_df = pd.read_csv(stable) if stable.exists() else pd.DataFrame()

    # Run the fetch pipeline in-memory by calling its public functions.
    new_df = fetch_data.fetch_cbinsights()
    source = "cbinsights"
    if new_df is None or len(new_df) < 50:
        new_df = fetch_data.fetch_wikipedia()
        source = "wikipedia"
    if new_df is None or new_df.empty:
        print("ERROR: could not fetch fresh data from either source.", file=sys.stderr)
        return 1

    new_df = fetch_data.normalize(new_df)
    diff = diff_frames(old_df, new_df)
    today = date.today().isoformat()
    diff_entry = {"date": today, "source": source, **diff}

    print(
        f"refresh diff [{today} / {source}]: "
        f"old={diff['n_old']} new={diff['n_new']} "
        f"+{diff['n_added']} -{diff['n_dropped']}"
    )
    if diff["added_sample"]:
        print(f"  added (sample): {diff['added_sample']}")
    if diff["dropped_sample"]:
        print(f"  dropped (sample): {diff['dropped_sample']}")

    if args.dry_run:
        print("dry-run: no files written")
        return 0

    # Persist: rotate prior stable -> prev, write new timestamped + new stable.
    if stable.exists():
        shutil.copyfile(stable, RAW_DIR / "unicorns_prev.csv")
    snap = RAW_DIR / f"unicorns_{today}.csv"
    new_df.to_csv(snap, index=False)
    shutil.copyfile(snap, stable)

    log_path = RAW_DIR / "_refresh_log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else []
    log.append(diff_entry)
    log_path.write_text(json.dumps(log, indent=2))

    print(f"wrote {snap.relative_to(REPO_ROOT)} and updated {stable.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
