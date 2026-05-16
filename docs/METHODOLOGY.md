# Methodology

This document is the formal write-up that backs every chart in this
repository. The README is the marketing copy; this is the methods
section. If a reader of one of the notebooks ever asks "where exactly
did this number come from and what would change it", the answer
should be in this file.

## 1. Scope

The repository asks narrow descriptive questions of **publicly
available** VC and startup data. It is deliberately separate from the
author's affiliation with the Stanford GSB Venture Capital Initiative
(VCI). No internal VCI dataset, sample frame, or derived field is used
here — only sources that any reader can re-fetch themselves with the
script in `scripts/fetch_data.py`.

The intent is not to publish new findings; it is to demonstrate
careful, reproducible work on the kind of data that public commentary
relies on every day.

## 2. Data sources

| Source                                  | Used for                                                    | Type        | URL                                                                  |
| --------------------------------------- | ----------------------------------------------------------- | ----------- | -------------------------------------------------------------------- |
| CB Insights unicorn tracker             | Current unicorn list: company, valuation, country, sector   | HTML scrape | https://www.cbinsights.com/research-unicorn-companies                |
| Wikipedia "List of unicorn startup companies" | Founder names; fallback unicorn list                  | HTML scrape | https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies      |
| Crunchbase (free tier)                  | Spot-checks of founding-year and founder names              | manual      | https://www.crunchbase.com/                                          |
| FRED                                    | Macro context (rates, M2, NASDAQ)                           | API         | https://fred.stlouisfed.org/                                         |
| SEC EDGAR                               | Filings for late-stage / post-IPO unicorns                  | API         | https://www.sec.gov/edgar/searchedgar/companysearch                  |
| OpenVC                                  | Investor / founder directory (free tier)                    | manual      | https://www.openvc.app/                                              |
| NVCA Yearbook (public summaries)        | Aggregate VC industry statistics                            | PDF         | https://nvca.org/research/nvca-yearbook/                             |

CB Insights is the primary source for the unicorn list. Wikipedia is
the fallback if CB Insights markup changes; it is also the only public
source that ships founder names for a meaningful subset of unicorns.

## 3. Pulling cadence

`scripts/fetch_data.py` is idempotent. It writes:

- `data/raw/unicorns_YYYY-MM-DD.csv` — timestamped snapshot
- `data/raw/unicorns.csv` — stable copy notebooks read
- `data/raw/founders.csv` — long-form Wikipedia founder rows
- `data/raw/_fetch_log.json` — provenance log (source, URL, row count, date)

`scripts/refresh_data.py` is the cadence script. It rotates the prior
stable copy to `unicorns_prev.csv`, pulls fresh, and writes a diff to
`data/raw/_refresh_log.json` so a reader can see which companies were
added or dropped between pulls without re-running the notebooks.

Pull cadence in practice: monthly. CB Insights itself updates roughly
monthly; pulling more often produces noise without information.

## 4. Schema

### `unicorns.csv`

| Column             | Type     | Source field                        | Notes                                                                 |
| ------------------ | -------- | ----------------------------------- | --------------------------------------------------------------------- |
| `company`          | string   | "Company"                           | Trimmed; not deduped against parent / subsidiary structure            |
| `valuation_usd_b`  | string   | "Valuation ($B)"                    | Kept as a string with the leading `$`; convert in-notebook            |
| `unicorn_year`     | Int64    | "Date Joined" (year extracted)      | Year company first crossed $1B per the tracker                        |
| `country`          | string   | "Country"                           | HQ country at listing time                                            |
| `City`             | string   | "City"                              | HQ city; pass-through                                                 |
| `sector`           | string   | "Industry"                          | CB Insights taxonomy; we collapse Industrial/Industrials              |
| `select_investors` | string   | "Select Investors"                  | Comma-joined free text                                                |

### `founders.csv`

| Column         | Type   | Notes                                       |
| -------------- | ------ | ------------------------------------------- |
| `company`      | string | Joins to `unicorns.csv:company` by exact match |
| `founder_name` | string | One row per (company, founder_name) pair    |

Coverage: roughly 200 of 1,300+ unicorns. Wildly skewed toward US/EU and
toward famous companies (see Notebook 04).

## 5. Known biases

The README lists these at a glance. Below is the long form.

### 5.1 Survivorship

The unicorn list is by construction a list of firms that crossed $1B
and have not been removed by the tracker. The denominator — every
startup ever founded, or every startup ever VC-backed — is unobserved
in these sources. Therefore:

- *Conditional* distributions ("among unicorns, X% are in Enterprise Tech") are well-defined.
- *Unconditional* rates ("X% of startups become unicorns") are **not** estimable here.
- "Years to unicorn" computed on the list is the years-to-unicorn of *surviving* unicorns; it cannot be read as expected years-to-unicorn for a new startup.

### 5.2 Reporting selection

Valuations come from voluntary disclosures, news leaks, and trackers.
Down-rounds and stealth devaluations are systematically under-reported.
"Paper unicorns" with stale 2021 marks remain on the list long after
their fair value has compressed. The tracker rarely demotes a company
once added.

### 5.3 Public-list lag

CB Insights and similar trackers add companies on a delay (median lag
between true unicorn date and listing date is on the order of months;
Notebook 04 quantifies this where possible). They rarely remove
companies. The minting-year distribution therefore *appears* heavier
in older cohorts than it would in a real-time pulse.

### 5.4 Geography coding

`country` is HQ location at listing time. It is **not** incorporation
country, founder origin, or primary operating geography. A company
re-domiciled to Singapore for tax reasons and a company built in
Singapore look identical here.

### 5.5 Founder-background proxies

Notebook 03 uses Wikipedia's `Founder(s)` cell as a public founder
record. Even on the covered subsample:

- "Listed solo" often means "only one founder publicly named", not "only one human founded the company". Co-founders who left in the first 1–2 years are routinely dropped.
- Coverage is biased toward English-language Wikipedia, which is biased toward US/EU. Cross-region comparisons of team size are contaminated by this.
- Demographic fields (gender, ethnicity, education) are not encoded in public sources in a way that supports honest measurement at scale.

## 6. How findings should be interpreted

Every notebook ends with a "what this cannot tell us" cell. Read that
section before citing a number. As a rule of thumb:

- Sector and geography *shares* of the current unicorn list are well-supported.
- Time-series of *minting years* are supported with the survivorship caveat.
- Cross-region statistics involving founders are not supported beyond directional sanity-checking.
- Anything that requires a denominator of all startups is not supported by this data.

## 7. What would change a finding

A short, explicit list of "if this were true, the analysis would change":

- **If founding-year coverage exceeded 80%** across all unicorns, the years-to-unicorn distribution by sector and cohort could be reported as a population statistic, not a subsample sanity check.
- **If the tracker published a removal log**, the minting-year time series could be corrected for survivorship in a transparent way.
- **If a structured hand-coded founder subsample were available** on a fixed frame (say 300 companies, stratified by region and cohort), the founder analyses in Notebook 03 could move from "directional" to "quantitative".
- **If CB Insights added a `verified_unicorn_date` field**, the lag between unicorn-status and listing could be corrected per-company instead of described in aggregate.

## 8. Reproducibility

```bash
# 60-second reproduction:
git clone https://github.com/mkzung/vc-pattern-notebooks.git
cd vc-pattern-notebooks
make setup
make fetch-data
make validate
make run-notebooks
```

Every figure is also written to `notebooks/figures/` so a reader who
does not want to run the code can still see the outputs.

## 9. Contact

For research collaborations involving non-public data, please reach
the author through Stanford GSB channels rather than this repository.
