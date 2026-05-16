"""Generate notebooks/04_data_quality_and_caveats.ipynb from a template.

This notebook is the methodological backbone for the rest of the
repo: every claim in notebooks 01-03 should be readable as
"true *within* the scope set in Notebook 04".

We build the notebook programmatically so the structure stays in
lockstep with the validation script and the methodology doc.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "notebooks" / "04_data_quality_and_caveats.ipynb"

CELLS: list[tuple[str, str]] = []  # (cell_type, source)


def md(s: str) -> None:
    CELLS.append(("markdown", s))


def code(s: str) -> None:
    CELLS.append(("code", s))


md(
    "# 04 - Data quality and caveats\n"
    "\n"
    "**Research question.** What can and cannot the public unicorn + founder data in this repo support? Concretely: how complete is each column, what is the quality of the sector taxonomy, how stale are entries on the tracker, and how heavily biased is the founder subsample?\n"
    "\n"
    "**Why this notebook exists.** Every other notebook in this repo (01-03) ends with a 'what this cannot tell us' cell. This notebook is the source of those caveats: every limitation in the other notebooks should be quantitatively reproducible from the cells below. If a future reader, reviewer, or grad-student wants to know whether a finding survives the data caveats, they should be able to point at one of the cells here.\n"
    "\n"
    "**Data sources.** Same as 01-03 - CB Insights public unicorn tracker and Wikipedia's `List_of_unicorn_startup_companies` table, pulled via `scripts/fetch_data.py`. Pull date and source recorded in `data/raw/_fetch_log.json`.\n"
)

md(
    "## Reproducibility\n"
    "\n"
    "Versions and pull metadata for the run that produced everything below. "
    "Also installs a `plt.show` hook that writes every figure to "
    "`notebooks/figures/` so the PNGs on GitHub stay in sync with the rendered notebook."
)

code(
    "# Reproducibility\n"
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
    "print('notebook    : 04_data_quality_and_caveats')\n"
    "\n"
    "_FIG_SLUG = '04_data_quality_and_caveats'\n"
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
    "plt.show = _show_and_save"
)

md(
    "## 1. Load both files\n"
    "\n"
    "We load the same two files that the other notebooks use, and snapshot the pull metadata. Everything in this notebook is conditional on this exact pull."
)

code(
    "from pathlib import Path\n"
    "import json\n"
    "import numpy as np\n"
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "\n"
    "sns.set_theme(style='whitegrid', context='talk')\n"
    "\n"
    "RAW = Path('..') / 'data' / 'raw'\n"
    "LOG = RAW / '_fetch_log.json'\n"
    "pull_meta = json.loads(LOG.read_text())[-1] if LOG.exists() else {'date': 'unknown', 'source': 'unknown'}\n"
    "\n"
    "df = pd.read_csv(RAW / 'unicorns.csv')\n"
    "fnd = pd.read_csv(RAW / 'founders.csv') if (RAW / 'founders.csv').exists() else pd.DataFrame()\n"
    "print(f\"unicorns.csv : {len(df):,} rows, {len(df.columns)} cols\")\n"
    "print(f\"founders.csv : {len(fnd):,} rows ({fnd['company'].nunique() if not fnd.empty else 0} unique companies)\")"
)

md(
    "## 2. Column completeness\n"
    "\n"
    "First, the simplest possible quality check: what fraction of rows is non-null in each column? Anything below 100% is a fact other notebooks have to handle (either drop, impute, or condition on).\n"
)

code(
    "completeness = (df.notna().mean() * 100).sort_values(ascending=True)\n"
    "completeness_table = completeness.round(1).to_frame('non_null_pct')\n"
    "completeness_table"
)

code(
    "fig, ax = plt.subplots(figsize=(10, 4.5))\n"
    "colors = ['#c44e52' if v < 95 else '#3b6fb6' for v in completeness.values]\n"
    "ax.barh(completeness.index, completeness.values, color=colors)\n"
    "for i, v in enumerate(completeness.values):\n"
    "    ax.text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=10)\n"
    "ax.set_xlim(0, 105)\n"
    "ax.set_xlabel('Non-null share (%)')\n"
    "ax.set_title('Column completeness in unicorns.csv')\n"
    "fig.text(0.01, -0.06,\n"
    "         f\"Source: {pull_meta['source']} public unicorn list, pulled {pull_meta['date']}. \"\n"
    "         'Bars below 95% (red) are columns where downstream notebooks must condition or drop.',\n"
    "         fontsize=8, style='italic')\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

md(
    "*Figure 1 - Column completeness in `data/raw/unicorns.csv`. Source: CB Insights public unicorn list, pulled on the date printed above. Columns below 95% non-null are flagged red; downstream notebooks must either condition on these columns being present or drop rows.*"
)

md(
    "## 3. Sector taxonomy quality\n"
    "\n"
    "CB Insights' sector field is free-form. Most rows land in one of seven clean buckets, but a small number have either typos, alternate spellings, or what look like city names that leaked into the sector column. The cell below surfaces every rare label so a reader can decide whether to re-code them by hand."
)

code(
    "sector_counts = df['sector'].fillna('(null)').value_counts()\n"
    "rare = sector_counts[sector_counts < 5]\n"
    "print(f'distinct sector labels : {sector_counts.size}')\n"
    "print(f'rare labels (n < 5)    : {rare.size}')\n"
    "rare.to_frame('n_rows')"
)

code(
    "# What share of rows is in the seven clean buckets?\n"
    "CANON = {\n"
    "    'Enterprise Tech',\n"
    "    'Financial Services',\n"
    "    'Consumer & Retail',\n"
    "    'Industrials',\n"
    "    'Healthcare & Life Sciences',\n"
    "    'Media & Entertainment',\n"
    "    'Insurance',\n"
    "}\n"
    "off_taxonomy = df.loc[~df['sector'].isin(CANON), 'sector'].fillna('(null)')\n"
    "print(f\"rows off the canonical taxonomy : {len(off_taxonomy)} / {len(df)} \"\n"
    "      f\"({len(off_taxonomy) / len(df):.2%})\")\n"
    "off_taxonomy.value_counts().head(20)"
)

md(
    "*Implication: ~0.2% of rows have sector labels that need hand-coding. The downstream notebooks bucket these into `Other` rather than dropping them; the bias from doing so is bounded by that share.*"
)

md(
    "## 4. Geographic coverage\n"
    "\n"
    "Two questions. First, what share of rows is in each region under the same coarse map used in 01 and 02. Second, where are the long-tail countries we are lumping into `Other`."
)

code(
    "REGION_MAP = {\n"
    "    'United States': 'US',\n"
    "    'China': 'CN', 'Hong Kong': 'CN',\n"
    "    'India': 'IN',\n"
    "    'United Kingdom': 'EU', 'Germany': 'EU', 'France': 'EU',\n"
    "    'Sweden': 'EU', 'Netherlands': 'EU', 'Spain': 'EU', 'Ireland': 'EU',\n"
    "    'Switzerland': 'EU', 'Estonia': 'EU', 'Finland': 'EU', 'Denmark': 'EU',\n"
    "    'Norway': 'EU', 'Italy': 'EU', 'Belgium': 'EU', 'Austria': 'EU',\n"
    "    'Portugal': 'EU', 'Luxembourg': 'EU', 'Czech Republic': 'EU',\n"
    "}\n"
    "df['region'] = df['country'].map(lambda c: REGION_MAP.get(str(c).strip(), 'Other') if pd.notna(c) else 'Other')\n"
    "region_share = (df['region'].value_counts(normalize=True) * 100).round(1)\n"
    "region_share.to_frame('share_pct')"
)

code(
    "# What's hiding in 'Other'? List the long tail.\n"
    "other_countries = df.loc[df['region'] == 'Other', 'country'].value_counts()\n"
    "print(f\"distinct countries in 'Other' bucket: {other_countries.size}\")\n"
    "other_countries.head(15).to_frame('n_unicorns')"
)

md(
    "*The `Other` bucket is not a small residual; it is around 10% of unicorns and contains real regional clusters (Israel, Canada, Brazil, Singapore, South Korea, Australia, Mexico). Any chart that compares US/CN/IN/EU/Other should be read with that in mind.*"
)

md(
    "## 5. Minting-year coverage and survivorship pressure\n"
    "\n"
    "CB Insights only lists current unicorns. The minting-year distribution is therefore not 'unicorns minted per year' but 'unicorns minted per year *and still listed today*'. The cell below visualizes that distribution; the asymmetry between older and newer cohorts is the survivorship pressure we cannot correct for from these sources alone."
)

code(
    "df['unicorn_year_num'] = pd.to_numeric(df['unicorn_year'], errors='coerce')\n"
    "valid = df.dropna(subset=['unicorn_year_num']).copy()\n"
    "valid['unicorn_year_num'] = valid['unicorn_year_num'].astype(int)\n"
    "yr_counts = valid['unicorn_year_num'].value_counts().sort_index()\n"
    "print(f\"unicorn_year non-null : {len(valid):,} / {len(df):,} ({len(valid)/len(df):.1%})\")\n"
    "print(f\"year range            : {yr_counts.index.min()} - {yr_counts.index.max()}\")\n"
    "yr_counts.tail(10).to_frame('n_unicorns')"
)

code(
    "fig, ax = plt.subplots(figsize=(11, 4.5))\n"
    "ax.bar(yr_counts.index, yr_counts.values, color='#3b6fb6', edgecolor='white')\n"
    "med = valid['unicorn_year_num'].median()\n"
    "ax.axvline(med, color='crimson', linestyle='--', linewidth=2,\n"
    "           label=f'median = {int(med)}')\n"
    "ax.set_xlabel('Year company first crossed $1B')\n"
    "ax.set_ylabel('Unicorns still listed today')\n"
    "ax.set_title('Survivorship-shaped minting-year distribution')\n"
    "ax.legend()\n"
    "fig.text(0.01, -0.06,\n"
    "         f\"Source: {pull_meta['source']} public unicorn list, pulled {pull_meta['date']}. \"\n"
    "         'Older cohorts have had more time to exit, fail, or be delisted; '\n"
    "         'low counts pre-2014 should NOT be read as few unicorns minted.',\n"
    "         fontsize=8, style='italic')\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

md(
    "*Figure 2 - Minting-year distribution among today's listed unicorns. Source: CB Insights, pulled on the date above. The leftward thinning is mostly attrition (exits, failures, delistings), not a real absence of unicorns minted before 2014.*"
)

md(
    "## 6. Tracker lag - how stale is the listing?\n"
    "\n"
    "If `unicorn_year` is, say, 2014 but the pull date is 2026, that listing has had 12 years to be wrong. We compute the gap between `unicorn_year` and the pull date as a proxy for staleness. Older listings carry more risk of 'paper unicorn' status (stale 2021 marks, etc.)."
)

code(
    "pull_year = int(pull_meta['date'][:4]) if pull_meta['date'] != 'unknown' else 2026\n"
    "valid['age_on_list'] = pull_year - valid['unicorn_year_num']\n"
    "age_summary = valid['age_on_list'].describe(percentiles=[0.25, 0.5, 0.75, 0.9]).round(1)\n"
    "print('Years since the company first crossed $1B (still listed):')\n"
    "print(age_summary)\n"
    "stale_share = (valid['age_on_list'] >= 5).mean()\n"
    "print(f\"\\nshare of entries that are >= 5 years old on the list : {stale_share:.1%}\")"
)

code(
    "fig, ax = plt.subplots(figsize=(10, 4.5))\n"
    "bins = range(0, int(valid['age_on_list'].max()) + 2)\n"
    "ax.hist(valid['age_on_list'], bins=bins, color='#3b6fb6', edgecolor='white')\n"
    "ax.axvline(5, color='crimson', linestyle='--', linewidth=2,\n"
    "           label='5-year staleness threshold')\n"
    "ax.set_xlabel('Years since unicorn_year (pull year - unicorn_year)')\n"
    "ax.set_ylabel('Number of listed unicorns')\n"
    "ax.set_title('Tracker staleness profile')\n"
    "ax.legend()\n"
    "fig.text(0.01, -0.06,\n"
    "         f\"Source: {pull_meta['source']} public unicorn list, pulled {pull_meta['date']}. \"\n"
    "         'The right tail is exposure to paper-unicorn risk.',\n"
    "         fontsize=8, style='italic')\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

md(
    "*Figure 3 - Distribution of (pull year - unicorn_year). Source: CB Insights, pulled on the date above. The right tail is the population most exposed to paper-unicorn risk (stale marks, undisclosed down-rounds).*"
)

md(
    "## 7. Founder coverage by region\n"
    "\n"
    "Notebook 03's founder analyses are conditional on Wikipedia having a `Founder(s)` cell for the company. The cell below quantifies that coverage by region. Anything < 30% is, in this repo's working definition, 'directional only' and should not be quoted as a population statistic."
)

code(
    "if not fnd.empty:\n"
    "    covered = set(fnd['company'].astype(str).str.strip())\n"
    "    df['has_founder_record'] = df['company'].astype(str).str.strip().isin(covered)\n"
    "    cov_by_region = (\n"
    "        df.groupby('region')['has_founder_record']\n"
    "          .agg(['mean', 'size'])\n"
    "          .rename(columns={'mean': 'covered_share', 'size': 'n_unicorns'})\n"
    "          .sort_values('covered_share', ascending=False)\n"
    "    )\n"
    "    print(cov_by_region.round(3))\n"
    "else:\n"
    "    cov_by_region = pd.DataFrame()\n"
    "    print('No founders.csv; skipping coverage-by-region.')"
)

code(
    "if not cov_by_region.empty:\n"
    "    fig, ax = plt.subplots(figsize=(9, 4.5))\n"
    "    order = cov_by_region.sort_values('covered_share').index\n"
    "    ax.barh(order, cov_by_region.loc[order, 'covered_share'], color='#3b6fb6')\n"
    "    for i, region in enumerate(order):\n"
    "        share = cov_by_region.loc[region, 'covered_share']\n"
    "        n = int(cov_by_region.loc[region, 'n_unicorns'])\n"
    "        ax.text(share + 0.005, i, f'{share:.0%} (n={n})', va='center', fontsize=10)\n"
    "    ax.axvline(0.30, color='crimson', linestyle='--', linewidth=2,\n"
    "               label='30% directional-only threshold')\n"
    "    ax.set_xlim(0, max(cov_by_region['covered_share']) * 1.4)\n"
    "    ax.set_xlabel('Share of unicorns with a public founder record')\n"
    "    ax.set_title('Founder-record coverage by region')\n"
    "    ax.legend()\n"
    "    fig.text(0.01, -0.06,\n"
    "             'Source: founder rows from Wikipedia (List_of_unicorn_startup_companies). '\n"
    "             'Below the dashed line, founder statistics are directional only.',\n"
    "             fontsize=8, style='italic')\n"
    "    plt.tight_layout()\n"
    "    plt.show()"
)

md(
    "*Figure 4 - Founder coverage by region. Every region is below 30%. Notebook 03 should therefore be read as a study of the covered subsample, not as a population-level statement about unicorn founders.*"
)

md(
    "## 8. Near-duplicate company names\n"
    "\n"
    "A common public-data trap: the same company appears twice under near-identical names (case, punctuation, suffixes). The cell below normalizes names and flags collisions. Anything surfaced here is a candidate for hand-coding."
)

code(
    "import re as _re\n"
    "def _norm(name: str) -> str:\n"
    "    s = str(name).lower().strip()\n"
    "    s = _re.sub(r\"[\\.,\\-'`]\", '', s)\n"
    "    s = _re.sub(r'\\b(inc|llc|ltd|corp|co|group|holdings?|technologies|technology|labs?|ai)\\b', '', s)\n"
    "    s = _re.sub(r'\\s+', ' ', s).strip()\n"
    "    return s\n"
    "\n"
    "df['name_norm'] = df['company'].apply(_norm)\n"
    "collisions = (\n"
    "    df.groupby('name_norm')\n"
    "      .agg(n_rows=('company', 'size'),\n"
    "           variants=('company', lambda s: sorted(set(s))),\n"
    "           countries=('country', lambda s: sorted(set(s.dropna()))))\n"
    "      .query('n_rows > 1')\n"
    "      .sort_values('n_rows', ascending=False)\n"
    ")\n"
    "print(f\"normalized-name collisions : {len(collisions)}\")\n"
    "collisions.head(15)"
)

md(
    "*Anything surfaced above is either a legitimate name collision (different companies, same brand) or a true duplicate. The validator in `scripts/validate_data.py` only fails when (company, country, sector, City) all match - looser keys are reviewed manually.*"
)

md(
    "## 9. What this data CAN and CANNOT support\n"
    "\n"
    "This is the section future readers should cite when they want to know whether a finding in 01-03 generalizes.\n"
    "\n"
    "**CAN support, with appropriate language:**\n"
    "\n"
    "- *Sector and geography composition of the current unicorn list* (notebooks 01, 02). The completeness numbers above show the underlying columns are >95% populated; the sector taxonomy is clean on ~99.8% of rows.\n"
    "- *Minting-year shape of today's surviving unicorns* (notebook 02), as long as the chart and caption both say 'surviving' or 'still listed'. The survivorship asymmetry visualized in section 5 is the irreducible caveat.\n"
    "- *Directional statements about founder team size on the covered subsample* (notebook 03), as long as the chart says 'covered' or 'Wikipedia subsample'. Founder coverage is below 30% in every region (section 7), so the result is not a population statistic.\n"
    "- *Coverage and bias measurement itself* - this notebook. The completeness numbers, taxonomy issues, and coverage gaps are publishable findings in their own right.\n"
    "\n"
    "**CANNOT support, even with caveats:**\n"
    "\n"
    "- *Unconditional rates of becoming a unicorn.* The denominator (every startup) is not in any of these sources.\n"
    "- *Years-to-unicorn for the unicorn population.* CB Insights does not publish founding year; the Wikipedia subsample with founding years (~200 / 1,300+) is too biased to ground a population statistic.\n"
    "- *Failure / down-round / demotion rates.* The tracker rarely removes companies; staleness in section 6 is the symptom.\n"
    "- *Cross-region comparisons of founder traits.* Coverage in section 7 is differentially biased toward US/EU.\n"
    "- *Causal claims of any kind.* Nothing in these data identifies a counterfactual.\n"
    "\n"
    "**What would change a finding** (long form in `docs/METHODOLOGY.md` section 7): if founding-year coverage exceeded 80% across the unicorn list, the years-to-unicorn distribution could be reported as a population statistic. If the tracker published a removal log, the minting-year time series could be corrected for survivorship transparently."
)

md(
    "## Save figures\n"
    "\n"
    "Figures are auto-persisted by the `plt.show` hook installed in the Reproducibility cell at the top. The cell below just lists what was written so the run is self-documenting."
)

code(
    "# Save key figures\n"
    "from pathlib import Path\n"
    "_slug = '04_data_quality_and_caveats'\n"
    "_written = sorted(Path('figures').glob(f'{_slug}_fig*.png'))\n"
    "print(f'{len(_written)} figure(s) saved to notebooks/figures/ for {_slug}:')\n"
    "for p in _written:\n"
    "    print(f'  {p}')"
)


def main() -> int:
    nb = nbf.v4.new_notebook()
    cells = []
    for kind, src in CELLS:
        if kind == "markdown":
            cells.append(nbf.v4.new_markdown_cell(src))
        elif kind == "code":
            cells.append(nbf.v4.new_code_cell(src))
        else:
            raise ValueError(kind)
    nb.cells = cells
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.11"},
    }
    nbf.write(nb, OUT)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
