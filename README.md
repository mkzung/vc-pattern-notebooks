# vc-pattern-notebooks

[![ci](https://github.com/mkzung/vc-pattern-notebooks/actions/workflows/ci.yml/badge.svg)](https://github.com/mkzung/vc-pattern-notebooks/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mkzung/vc-pattern-notebooks/main?urlpath=lab/tree/notebooks)
[![Open In Colab — 01](https://img.shields.io/badge/colab-01-orange?logo=googlecolab)](https://colab.research.google.com/github/mkzung/vc-pattern-notebooks/blob/main/notebooks/01_unicorn_geography_and_sector.ipynb)
[![Open In Colab — 02](https://img.shields.io/badge/colab-02-orange?logo=googlecolab)](https://colab.research.google.com/github/mkzung/vc-pattern-notebooks/blob/main/notebooks/02_time_to_unicorn.ipynb)
[![Open In Colab — 03](https://img.shields.io/badge/colab-03-orange?logo=googlecolab)](https://colab.research.google.com/github/mkzung/vc-pattern-notebooks/blob/main/notebooks/03_founder_patterns_proxy.ipynb)
[![Open In Colab — 04](https://img.shields.io/badge/colab-04-orange?logo=googlecolab)](https://colab.research.google.com/github/mkzung/vc-pattern-notebooks/blob/main/notebooks/04_data_quality_and_caveats.ipynb)

> Reproducible analyses of patterns in venture capital and startup outcomes using **only public data**. Companion notebooks to ongoing research; for confidential research outputs, see [VCI publications](https://www.gsb.stanford.edu/faculty-research/labs-initiatives/vci).

---

## Findings preview

Each line links to the figure that backs it. Numbers are conditional on the pull date recorded in `data/raw/_fetch_log.json` (most recent: 1,356 unicorns from CB Insights, 2026-05-16).

- **Enterprise Tech share of new unicorns roughly tripled across cohorts.** From ~14% of the 2014–2017 minting cohort to ~40% of the 2021+ cohort. ([fig](notebooks/figures/01_unicorn_geography_and_sector_fig1.png))
- **The unicorn list is dominated by four geographies plus a real tail.** US ~58%, CN ~12%, EU ~9%, IN ~5%, "Other" ~17% — and "Other" hides Israel, Canada, Brazil, Singapore, South Korea. ([fig](notebooks/figures/01_unicorn_geography_and_sector_fig2.png))
- **Today's unicorn list is overwhelmingly recent.** ~81% of currently-listed unicorns crossed $1B in 2020 or later; only ~1% were minted between 2007 and 2014. Most of that asymmetry is survivorship, not absence. ([fig](notebooks/figures/02_time_to_unicorn_fig1.png), [staleness](notebooks/figures/04_data_quality_and_caveats_fig3.png))
- **Public founder coverage is below 30% in every region.** Wikipedia's `Founder(s)` cell covers ~12% of US unicorns, ~27% of Indian unicorns, ~3% of Chinese unicorns. Cross-region founder statistics are not population-level. ([fig](notebooks/figures/04_data_quality_and_caveats_fig4.png))

Every claim above has a "what this cannot tell us" cell in the notebook it comes from. Read Notebook 04 before quoting any number.

## How to reproduce in 60 seconds

```bash
git clone https://github.com/mkzung/vc-pattern-notebooks.git
cd vc-pattern-notebooks
make setup         # pip install -r requirements.lock
make fetch-data    # public unicorn + founder pulls into data/raw/
make validate      # scripts/validate_data.py — exits 1 on schema drift
make run-notebooks # nbconvert --execute on all four notebooks
```

If you only want to *read* outputs without running anything, every chart is committed under [`notebooks/figures/`](notebooks/figures/) and the executed notebooks render directly on GitHub.

## Thesis

Most public commentary on venture capital relies on selective anecdote. A growing body of public data — unicorn lists, regulatory filings, macroeconomic indicators, founder-database scrapes — is good enough to surface real patterns, *if* you are explicit about what the data can and cannot tell you. This repo is an open lab notebook: each notebook poses one narrow question, pulls a public dataset, and ends with an honest "what this cannot tell us" section. Notebook 04 (`04_data_quality_and_caveats.ipynb`) is the methodological backbone — start there if you want to know which numbers in this repo generalize.

It is deliberately **separate** from my work at the [Stanford Venture Capital Initiative](https://www.gsb.stanford.edu/faculty-research/labs-initiatives/vci) (Prof. Ilya Strebulaev's lab). No internal VCI datasets, sample frames, or proprietary fields are used here — only sources anyone can re-fetch.

## Data sources (public only)

| Source | What we use it for | URL |
| --- | --- | --- |
| CB Insights unicorn tracker | Current unicorn list with valuation, country, sector | https://www.cbinsights.com/research-unicorn-companies |
| Wikipedia unicorn list (mirror / fallback) | Stable scrapable mirror when CB Insights lacks an API | https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies |
| Crunchbase (free tier) | Spot-checking founding years and founder names | https://www.crunchbase.com/ |
| FRED (St. Louis Fed) | Macro context: rates, M2, NASDAQ levels | https://fred.stlouisfed.org/ |
| SEC EDGAR | S-1 / 10-K filings for late-stage / post-IPO unicorns | https://www.sec.gov/edgar/searchedgar/companysearch |
| OpenVC | Investor and founder directory (free tier) | https://www.openvc.app/ |
| NVCA Yearbook (public summaries) | Aggregate VC industry statistics | https://nvca.org/research/nvca-yearbook/ |

Full provenance (pull date, source URL, row count) is logged to `data/raw/_fetch_log.json` on every fetch. The formal methodology write-up lives in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

## Notebooks

| # | Notebook | One-line summary |
| --- | --- | --- |
| 01 | [`notebooks/01_unicorn_geography_and_sector.ipynb`](notebooks/01_unicorn_geography_and_sector.ipynb) | Sector mix over time, US/CN/IN/EU/Other concentration, and a sector × geography heatmap. |
| 02 | [`notebooks/02_time_to_unicorn.ipynb`](notebooks/02_time_to_unicorn.ipynb) | Years from founding to $1B status, broken out by sector and founding-year cohort. |
| 03 | [`notebooks/03_founder_patterns_proxy.ipynb`](notebooks/03_founder_patterns_proxy.ipynb) | Solo-vs-team founding, repeat-founder share, and a public-bio proxy for founder background. |
| 04 | [`notebooks/04_data_quality_and_caveats.ipynb`](notebooks/04_data_quality_and_caveats.ipynb) | **Read this before citing anything.** Completeness, taxonomy issues, staleness, founder-coverage bias, what the data CAN and CANNOT support. |

Each notebook ships with:

- a **Reproducibility** cell at the top that prints `pandas`, `numpy`, `matplotlib` versions and the data pull date,
- a **Save figures** hook that mirrors every `plt.show()` to `notebooks/figures/<NN>_<slug>_figN.png`,
- a **what this cannot tell us** section at the bottom.

## Repository layout

```
.
├── .github/workflows/ci.yml      validate + execute notebooks + lint
├── binder/                       requirements.txt + runtime.txt for mybinder.org
├── data/
│   ├── README.md                 what lives here, what does not
│   └── raw/                      gitignored, populated by scripts/fetch_data.py
│       ├── sample_unicorns.csv   CI fixture (committed)
│       └── sample_founders.csv   CI fixture (committed)
├── docs/METHODOLOGY.md           formal methods write-up
├── notebooks/
│   ├── 01_*.ipynb … 04_*.ipynb   the four analyses
│   └── figures/                  PNGs of every matplotlib figure, kept in sync
├── scripts/
│   ├── fetch_data.py             public-data pull
│   ├── refresh_data.py           timestamped re-pull + diff log
│   └── validate_data.py          schema + completeness + duplicate checks
├── .python-version               3.11
├── Makefile                      setup / fetch-data / validate / run-notebooks / lint
├── pyproject.toml                package metadata
├── requirements.txt              top-level deps
└── requirements.lock             pinned lockfile (uv pip compile)
```

## Methodology & limitations

**This repository uses public data only.** It does not, and will not, include any confidential datasets, sample frames, or derived fields associated with the Stanford VCI / Strebulaev research group. Confidential analyses live elsewhere and are published through peer-reviewed channels.

Known biases of public VC data (not exhaustive — see [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) section 5 for the long form):

- **Survivorship.** Public unicorn lists by construction include only firms that crossed $1B. The denominator — every startup ever founded — is unobserved. Conditional distributions ("among unicorns, X% are AI") are well-defined; unconditional rates ("X% of startups become unicorns") are not estimable from these sources alone.
- **Reporting selection.** Valuations come from voluntary disclosures, news leaks, and trackers. Down-rounds and stealth devaluations are systematically under-reported.
- **Public-list lag.** CB Insights and similar trackers add companies on a delay and rarely remove them; a unicorn that quietly fails may linger for quarters.
- **Geography coding.** "Country" usually reflects HQ location at time of listing, not incorporation, founder origin, or operating geography.
- **Founder-background proxies** (Notebook 03) rely on LinkedIn-style public bios and are biased toward English-language, US/EU coverage. Quantified in Notebook 04 section 7.

Where these biases matter for a given chart, the notebook says so in markdown adjacent to the figure.

## Citation

If these analyses or the methodology informs your work, please cite as:

```bibtex
@misc{gorbuk_vc_pattern_notebooks,
  author       = {Gorbuk, Max},
  title        = {vc-pattern-notebooks: reproducible analyses of public venture-capital data},
  year         = {2026},
  howpublished = {\url{https://github.com/mkzung/vc-pattern-notebooks}},
  note         = {Companion notebooks; methodology in docs/METHODOLOGY.md.}
}
```

## License

MIT — see [`LICENSE`](LICENSE).

## Contact

Max Gorbuk — Researcher, Stanford GSB Venture Capital Initiative. Issues and PRs welcome. For research collaborations involving non-public data, please reach out through Stanford GSB channels rather than this repo.
