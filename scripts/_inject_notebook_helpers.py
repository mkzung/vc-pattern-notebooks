"""One-off helper that injects standard cells into the notebooks.

Adds, idempotently:
  - a 'Reproducibility' markdown+code pair right after the title cell
  - a 'Save figures' code block at the end that walks plt.get_fignums()
    and writes each figure to notebooks/figures/<NN>_<slug>_figN.png
  - tagged captions on each plotting cell are left to the author —
    this script only handles the bookend cells.

Run from the repo root:

    python scripts/_inject_notebook_helpers.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat

REPO_ROOT = Path(__file__).resolve().parents[1]
NB_DIR = REPO_ROOT / "notebooks"

REPRO_MARKER = "# Reproducibility"
SAVE_MARKER = "# Save key figures"


def repro_cells(slug: str) -> list[nbformat.NotebookNode]:
    md = nbformat.v4.new_markdown_cell(
        "## Reproducibility\n\n"
        "The cell below records the package versions and the data-pull "
        "metadata that produced everything below. It also installs a "
        "hook so every `plt.show()` call also writes the figure to "
        "`notebooks/figures/` — that way the PNGs on GitHub are always "
        "in sync with the rendered notebook."
    )
    code = nbformat.v4.new_code_cell(
        f"{REPRO_MARKER}\n"
        "from __future__ import annotations\n"
        "import json, sys\n"
        "from pathlib import Path\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "import matplotlib\n"
        "import matplotlib.pyplot as plt\n"
        "_log = Path('..') / 'data' / 'raw' / '_fetch_log.json'\n"
        "_meta = json.loads(_log.read_text())[-1] if _log.exists() else {'date': 'unknown', 'source': 'unknown'}\n"
        "print(f'python      : {sys.version.split()[0]}')\n"
        "print(f'pandas      : {pd.__version__}')\n"
        "print(f'numpy       : {np.__version__}')\n"
        "print(f'matplotlib  : {matplotlib.__version__}')\n"
        "print(f'data source : {_meta.get(\"source\")}')\n"
        "print(f'pull date   : {_meta.get(\"date\")}')\n"
        f"print('notebook    : {slug}')\n"
        "\n"
        f"_FIG_SLUG = '{slug}'\n"
        "_FIG_DIR = Path('figures'); _FIG_DIR.mkdir(parents=True, exist_ok=True)\n"
        "_FIG_COUNTER = {'n': 0}\n"
        "_orig_show = plt.show\n"
        "def _show_and_save(*a, **kw):\n"
        "    for num in plt.get_fignums():\n"
        "        _FIG_COUNTER['n'] += 1\n"
        "        fig = plt.figure(num)\n"
        "        out = _FIG_DIR / f'{_FIG_SLUG}_fig{_FIG_COUNTER[\"n\"]}.png'\n"
        "        fig.savefig(out, dpi=140, bbox_inches='tight')\n"
        "    return _orig_show(*a, **kw)\n"
        "plt.show = _show_and_save\n"
    )
    return [md, code]


def save_figures_cells(slug: str) -> list[nbformat.NotebookNode]:
    md = nbformat.v4.new_markdown_cell(
        "## Save figures\n\n"
        "Figures are auto-persisted by the `plt.show` hook installed in "
        "the Reproducibility cell at the top. The cell below just lists "
        "what was written so the run is self-documenting. Plotly figures "
        "are interactive and not exported here."
    )
    code = nbformat.v4.new_code_cell(
        f"{SAVE_MARKER}\n"
        "from pathlib import Path\n"
        f"_slug = '{slug}'\n"
        "_written = sorted(Path('figures').glob(f'{_slug}_fig*.png'))\n"
        "print(f'{len(_written)} figure(s) saved to notebooks/figures/ for {_slug}:')\n"
        "for p in _written:\n"
        "    print(f'  {p}')\n"
    )
    return [md, code]


def has_marker(cells, marker: str) -> bool:
    return any(c.cell_type == "code" and marker in c.source for c in cells)


def slug_for(path: Path) -> str:
    # e.g. 01_unicorn_geography_and_sector
    return path.stem


def _strip_pair(cells, marker: str) -> tuple[list, int | None]:
    """Remove an existing (markdown, code) pair where the code has marker.

    Returns (new_cells, position_where_pair_was) so the caller can
    reinsert fresh cells at the same spot."""
    for idx, c in enumerate(cells):
        if c.cell_type == "code" and marker in c.source:
            # Drop the marker code cell and its preceding markdown if any.
            start = idx - 1 if idx > 0 and cells[idx - 1].cell_type == "markdown" else idx
            return cells[:start] + cells[idx + 1 :], start
    return cells, None


def inject(path: Path) -> None:
    nb = nbformat.read(path, as_version=4)
    cells = list(nb.cells)
    slug = slug_for(path)

    # Reproducibility pair - always rewrite so the hook stays current.
    cells, repro_pos = _strip_pair(cells, REPRO_MARKER)
    insert_at = repro_pos if repro_pos is not None else (
        1 if cells and cells[0].cell_type == "markdown" else 0
    )
    for i, c in enumerate(repro_cells(slug)):
        cells.insert(insert_at + i, c)
    print(f"  ~ refreshed reproducibility cells in {path.name}")

    # Save-figures pair - always at the end.
    cells, _ = _strip_pair(cells, SAVE_MARKER)
    cells.extend(save_figures_cells(slug))
    print(f"  ~ refreshed save-figures cells in {path.name}")

    nb.cells = cells
    nbformat.write(nb, path)


def main() -> int:
    for nb_path in sorted(NB_DIR.glob("*.ipynb")):
        if "_tmp" in nb_path.name:
            continue
        inject(nb_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
