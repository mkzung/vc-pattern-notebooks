# data/

This directory holds locally cached copies of **public** datasets used by the notebooks.

## Layout

```
data/
├── README.md          # you are here
└── raw/               # gitignored — populated by scripts/fetch_data.py
    └── .gitkeep
```

`data/raw/` is **gitignored**. Nothing in it is committed to the repository. To populate it on a fresh clone:

```bash
python scripts/fetch_data.py
```

That script writes timestamped files such as `data/raw/unicorns_YYYY-MM-DD.csv` and a stable symlink/copy at `data/raw/unicorns.csv` that the notebooks load.

## What lives here

| File | Source | Refreshed by |
| --- | --- | --- |
| `unicorns.csv` | CB Insights unicorn tracker (with Wikipedia fallback) | `scripts/fetch_data.py` |

## What does NOT live here

This repository does **not** mirror, cache, or otherwise redistribute any non-public dataset. In particular, no data associated with the Stanford VCI / Strebulaev research group is present in this folder or anywhere else in the repo. If you find something in `data/` that looks like it came from a paid or restricted source, please open an issue.
