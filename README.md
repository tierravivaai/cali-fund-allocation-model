# Cali Fund Allocation Model (Inverted UN Scale Option)

This repository contains all the code, data and tests used to create the Inverted UN Scale of Assessments Formula (IUSAF) model as an option for consideration by the Ad Hoc Technical Expert Group on the Allocation Methodology for the Cali Fund established under the Convention on Biological Diversity by decision 16/2. The repository elaborates what is called Option A: The Inverted UN Scale of Assessments for consideration by the AHTEG.

The objective is to create a simple and easy to communicate allocation formula. The central idea is that the Cali Fund allocation will be made based on recognition of a Party's economic capacity and biodiversity stewardship responsibilities. In its simplest form the allocation formula reads: 

> Country Share = economic capacity + biodiversity stewardship

The formula works in an innovative way. The United Nations core budget is set by the Contributions Committee through the United Nations Scale of Assessments and is agreed by the General Assembly every three years (currently 2025-2027). Under the UN Scale, developing countries and least developed countries make smaller contributions and member states with higher economic capacity make larger contributions. The proposed formula for the Cali Fund allocation turns the UN Scale on its head and inverts the UN Scale so that Parties to the CBD with lower agreed economic capacity will receive a higher allocation from the Cali Fund. Parties with higher agreed economic capacity under the UN Scale will receive a lower allocation from the Cali Fund. This is achieved by organising 142 CBD Parties into six weighted bands using the UN Scale where Parties in lower bands receive a larger allocation than Parties in higher bands (so that band 1 receives more than band 2 and so on until band 6). This approach favours least developed and lower income developing countries.

The formula also recognises that different Parties to the CBD have different biodiversity stewardship responsibilities that reflect their biogeographic characteristics. Small Island Developing States (SIDS) are formally recognised by the United Nations for the structural challenges that they face. SIDS also hold responsibility for stewardship of large ocean areas. In a similar way, some middle income Parties hold biodiversity stewardship responsibilitites for very large and diverse biogeographic ecosystems.

The formula recognises these biodiversity stewardship responsibilities through a SIDS Ocean Stewardship Component (SOSAC) and Terrestrial Stewardship Component (TSAC). These are overlays on top of the allocation by economic capacity that reallocate a pool of funds to recognise stewardship.

Indigenous Peoples and Local Communities play a vital role in the conservation and sustainable use of biodiversity. The formula treats Indigenous Peoples and Local Communities as integral and divides the geographic country allocation equally between the state and Indigenous Peoples and Local Communities. The formula includes an allocation for Indigenous Peoples and Local Communities in developed countries.  

That formula can be easily expressed in plain English as follows:

> The Cali Fund Allocation formula is based on an inverted United Nations Scale of Assessments used to determine member states contributions to the UN core budget. It includes components recognising the different ocean and terrestrial biodiversity stewardship responsibilities among Parties. Recognition of the vital role of indigenous peoples and local communities for the conservation and sustainable use of biodiversity is integral to the formula.

As a formula this can be expressed at different levels of detail for different audiences:

    Country Share = economic capacity + biodiversity stewardship

OR

    Country Share = Inverted UN Scale + Ocean Stewardship + Terrestrial Stewardship

OR with acronyms:
        
    Country Share = IUSAF + SOSAC + TSAC	

OR using mathematical symbols for TSAC (β) and SOSAC (γ):

    Country Shareᵢ = (1 − β − γ) × IUSAFᵢ + β × TSACᵢ + γ × SOSACᵢ

Where the subscript ᵢ denotes that each component value is computed per Party. Every eligible CBD Party receives its own share based on its individual IUSAF weight (economic capacity), land area (TSAC), and SIDS status (SOSAC). The weights β and γ are global parameters and the per-Party component values vary across countries.

An important strength of the simple approach is that it does not require mathematical symbols to explain it. Where the formal expression helps is in making clear that the stewardship pool is created by **reallocating funds** from the equity base of the Inverted UN Scale (IUSAF) to the stewardship components. If the use of the inverted UN Scale is accepted as the foundation for the allocation formula the key challenge becomes deciding on the size of the stewardship pool. 

This repository contains the background datasets used in the calculation of options
under the formula by individual country and United Nations region. It contains two streamlit applications (one for the country tables and one for sensitivity testing). 

The formula application is available online at [https://cali-fund-allocation-model.streamlit.app/](https://cali-fund-allocation-model.streamlit.app/) and can be woken from 


As is explained below this repository was written by Dr. Paul Oldham using advanced AI software engineering tools, notably [Droid from Factory AI](https://factory.ai/), and a number of different AI models. The key advantage of the use of AI is speed and rigour because testing, validation and peer review of code can all be automated. You will find a very detailed set of unit tests (testing code) and a sensitivity test suite (testing the model). Instructions on cloning and running the repository and its applications is provided below. 

## Key Document Outputs

1. The Working Paper in Word can be downloaded [here](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/docs/working_papers/iusaf_paper-07052026.docx) or as [PDF](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/docs/working_papers/iusaf_paper-07052026.pdf)
2. Tables in the working paper are generated from the live calculator and validated against CSV references. See [Table Sources](#table-sources) below.
3. Country Annexes are provided for the various balance points
at different scales of the Cali Fund (see [country-annexes](https://github.com/tierravivaai/cali-fund-allocation-model/tree/main/country-annexes)). Combined annexes per fund size: [$50M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/fifty-million/country-annexes-fifty-million.docx), [$200M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/two-hundred-million/country-annexes-two-hundred-million.docx), [$500M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/five-hundred-million/country-annexes-five-hundred-million.docx), [$1 billion](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/one-billion/country-annexes-one-billion.docx)
- Pure Inverted Scale: [$50M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/fifty-million/iusaf-pure/iusaf-pure-country-annex.docx), [$200M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/two-hundred-million/iusaf-pure/iusaf-pure-country-annex.docx), [$500M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/five-hundred-million/iusaf-pure/iusaf-pure-country-annex.docx), [$1 billion](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/one-billion/iusaf-pure/iusaf-pure-country-annex.docx)
- Strict: [$50M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/fifty-million/iusaf-strict/iusaf-strict-country-annex.docx), [$200M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/two-hundred-million/iusaf-strict/iusaf-strict-country-annex.docx), [$500M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/five-hundred-million/iusaf-strict/iusaf-strict-country-annex.docx), [$1 billion](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/one-billion/iusaf-strict/iusaf-strict-country-annex.docx)
- Gini-minimum: [$50M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/fifty-million/gini-minimum/gini-minimum-country-annex.docx), [$200M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/two-hundred-million/gini-minimum/gini-minimum-country-annex.docx), [$500M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/five-hundred-million/gini-minimum/gini-minimum-country-annex.docx), [$1 billion](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/one-billion/gini-minimum/gini-minimum-country-annex.docx)
- Band-Order Boundary: [$50M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/fifty-million/band-order-boundary/band-order-boundary-country-annex.docx), [$200M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/two-hundred-million/band-order-boundary/band-order-boundary-country-annex.docx), [$500M](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/five-hundred-million/band-order-boundary/band-order-boundary-country-annex.docx), [$1 billion](https://github.com/tierravivaai/cali-fund-allocation-model/raw/refs/heads/main/country-annexes/one-billion/band-order-boundary/band-order-boundary-country-annex.docx)

## The Formula

The approach to the allocation formula deliberately avoids the use of mathematical notation in favour of ease of communication. However, the formula can be formally expressed as:  

**Country Shareᵢ = (1 − β − γ) × IUSAFᵢ + β × TSACᵢ + γ × SOSACᵢ**

The subscript ᵢ denotes a per-Party calculation: each component value differs by country.

- **IUSAF**: Inverted UN Scale — the equity base, tilted towards lower-income and LDC countries.
- **TSAC**: Terrestrial Stewardship — proportional to land area (km²).
- **SOSAC**: SIDS Ocean Stewardship — equal-share pool for eligible Small Island Developing States
.
- **β, γ**: Global overlay weights applied uniformly across all Parties. **The central policy question is where to set the balance between the equity base and the stewardship overlays.**

→ Full methodology: [reference/methodology.md](reference/methodology.md)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main negotiation app
streamlit run src/app.py

# Run the sensitivity/robustness app
streamlit run src/sensitivity.py
```

## Table Sources

Tables in the working paper (`iusaf_paper-07052026.docx`) are generated from the live DuckDB calculator used in the application and validated against reference CSVs. The table numbering below refers to the paper's internal numbering.

| Paper Table | Content | Generator Script | Validated CSV |
|---|---|---|---|
| 1 | Six-band IUSAF configuration | `src/cali_model/calculator.py` | `config/un_scale_bands.yaml` |
| 2 | Allocation by UN Region | `scripts/validate_all_tables.py` → `gen_region_table()` | `model-tables/iusaf-unregion-15042026.csv` |
| 3 | Allocation by UN Sub-Region | `scripts/validate_all_tables.py` → `gen_subregion_table()` | `model-tables/iusaf-unsubregion-15042026.csv` |
| 4 | Allocation by Intermediate Region | `scripts/validate_all_tables.py` → `gen_intermediate_region_table()` | `model-tables/iusaf-unintermediate-region-15042026.csv` |
| 5 | LDC allocation panel | `scripts/validate_all_tables.py` → `gen_ldc_sids_panel()` | `model-tables/iusaf-ldc-panel-16042026.csv` |
| 6 | SIDS allocation panel | `scripts/validate_all_tables.py` → `gen_ldc_sids_panel()` | `model-tables/iusaf-sids-panel-16042026.csv` |
| 7 | Top 31 parties by allocation | `scripts/validate_all_tables.py` → `gen_ranked_country_table()` | `model-tables/iusaf-ranked-country-16042026.csv` |
| 8 | Bottom 22 parties by allocation | `scripts/validate_all_tables.py` → `gen_ranked_country_table()` | `model-tables/iusaf-ranked-country-16042026.csv` |
| 9 | Middle 89 parties by allocation | `scripts/validate_all_tables.py` → `gen_ranked_country_table()` | `model-tables/iusaf-ranked-country-16042026.csv` |
| 10 | SIDS band distribution (SOSAC impact) | `src/cali_model/calculator.py` | `model-tables/iusaf-sids-countries-15042026.csv` |
| 11 | SOSAC per-SIDS by band | `src/cali_model/calculator.py` | `model-tables/iusaf-sids-panel-16042026.csv` |
| 12 | Land area (TSAC input) top 20 | `src/cali_model/calculator.py` | `model-tables/iusaf-band-order-preservation.csv` |
| 13 (E1) | Component allocation by balance point & fund size | `scripts/generate_tsac_section_draft.py` | Computed live from `cali_model` |
| 14 (E2) | Stewardship pool by balance point & fund size | `scripts/generate_tsac_section_draft.py` | Computed live from `cali_model` |
| 15 (A) | Band-order preservation across TSAC levels | `scripts/generate_optiond_tables.py` → `write_band_order_table()` | `model-tables/iusaf-band-order-preservation.csv` |
| 16 (B) | TSAC break-point summary | `scripts/generate_optiond_tables.py` → `write_breakpoint_summary_table()` | `model-tables/iusaf-breakpoint-summary.csv` |
| 17 (C) | Full TSAC ranking trajectory | `src/cali_model/balance_analysis.py` | `model-tables/iusaf-breakpoint-summary.csv` |
| 18 (D1) | IUSAF band composition | `src/cali_model/calculator.py` | Computed live |
| 19 (D2) | Change in band allocation vs pure IUSAF | `src/cali_model/calculator.py` | Computed live |
| 20 | IPLC developed-country Option 1 (equality) | `iplc-developed/` test-verified | `iplc-developed/iplc-option1-equality-*.csv` |
| 21 | IPLC developed-country Option 2 (banded) | `iplc-developed/` test-verified | `iplc-developed/iplc-option2-banded-*.csv` |
| 22–25 | Country annexes (4 scenarios × $1B) | `country-annexes/generate_all_fund_sizes.py` | Per-scenario CSVs in `country-annexes/{fund}/{scenario}/` |

All validation CSVs are in `model-tables/table-validation/`. The validation script is `scripts/validate_all_tables.py`.

## Repository Structure

```
├── src/                          # Application and model code
│   ├── app.py                    # Main Streamlit negotiation app
│   ├── sensitivity.py            # Sensitivity analysis & reporting app
│   └── cali_model/               # Core calculation library
│       ├── calculator.py         # calculate_allocations() and aggregation functions
│       ├── data_loader.py        # DuckDB-based ETL (raw data → base_df)
│       ├── balance_analysis.py   # Fine sweeps, Gini-minimum identification
│       ├── sensitivity_metrics.py # Gini, Spearman, component ratios
│       ├── sensitivity_scenarios.py # Scenario definitions and two-way grids
│       └── reporting.py          # Markdown/CSV export generation
│
├── tests/                        # Pytest suite (178+ tests)
│   ├── test_logic.py             # Party count, inversion, allocation sums
│   ├── test_band_inversion.py    # Band assignment and weight validation
│   ├── test_tsac_sosac.py       # Component blending and isolation
│   ├── test_totals.py            # Aggregation (region, income, LDC, SIDS)
│   ├── test_floor_ceiling.py     # Constraint redistribution
│   ├── test_equality_mode.py    # Equality mode switching
│   ├── test_tiny_scenarios.py   # Fund conservation at extreme sizes
│   ├── test_negotiator_dashboard.py # Baseline comparisons
│   ├── test_ui_reset.py         # Preset and reset behaviour
│   └── ...                       # 16 more test modules
│
├── scripts/                      # Standalone generation scripts
│   ├── generate_balance_point_rankings.py  # Balance-point tables
│   ├── generate_optiond_tables.py         # Option D threshold tables
│   ├── generate_tsac_section_draft.py      # TSAC section Word output
│   ├── generate_all_fund_sizes.py          # Country annex generation
│   ├── validate_all_tables.py              # Table validation against live calculator
│   └── ...                                 # Cross-check and export scripts
│
├── config/                       # Model configuration
│   └── un_scale_bands.yaml       # 6-band UN scale weights
│
├── data-raw/                     # Source data (CSV/XLSX)
│   ├── UNGA_scale_of_assessment.csv   # UN Scale 2025–2027
│   ├── cbd_cop16_budget_table.csv     # CBD Party list (source of truth)
│   ├── manual_name_map.csv           # Party name concordance
│   ├── CLASS_2025_10_07.xlsx         # World Bank income groups
│   └── ...                           # Land area, EU, UNSD regions
│
├── model-tables/                 # Generated output tables (CSV, MD) + table-validation/
├── iplc-developed/               # IPLC developed-country analysis
│   ├── specification.md           # Option 1 & 2 specification
│   ├── iplc-option1-equality.md    # Option 1 analysis and CSVs
│   ├── iplc-option2-banded.md     # Option 2 analysis and CSVs
│   ├── test_structural_validation.py # 40 structural validation tests
│   └── validation_analysis.md    # Why Option 1 ≈ Option 2
│
├── country-annexes/              # Country annex DOCX tables (4 scenarios × 4 fund sizes)
├── sensitivity-reports/          # Generated sensitivity outputs (v4)
├── band-analysis/                 # Break-point and stewardship pool analysis
├── figures/                       # Plots and visualisations (UN scale distribution, contribution bands)
├── reference/                     # Detailed documentation
│   ├── methodology.md             # Formula, bands, balance points
│   ├── data-sources.md            # Data pipeline and sources
│   └── validation.md              # Test suite and integrity checks
│
├── deprecated/                   # Retired content (instructions, v3 reports, Spearman threshold)
├── docs/                         # Working paper and supporting markdown
│
├── requirements.txt               # Python dependencies
├── change_log.md                  # Versioned change history
└── AGENTS.md                     # AI agent instructions
```

## Application Layers

### `app.py` — Main Negotiation App

The primary interactive interface for exploring policy scenarios.

**Features:**
- Adjustable fund size ($2m–$10bn), IPLC split (50–80%), TSAC (0–15%), SOSAC (0–10%)
- Five negotiation presets: Equality, Inverted UN Scale, Terrestrial Stewardship, Oceans Stewardship, Gini-minimum point
- Band-based inversion (default) or raw inversion mode
- High-income country exclusion (off by default for equality start)
- Optional floor and ceiling constraints
- **Negotiation Dashboard**: increases/decreases vs baseline, group impact charts, per-country waterfall, stewardship scenario comparison
- Multi-perspective tabs: By Party, By Region, By Income Group, LDC, SIDS, Inversion Comparison
- Plain-language and technical explanation toggles
- Blend warnings when stewardship weights become strong or overriding

### `sensitivity.py` — Sensitivity & Robustness App

Dedicated parameter-sweep and reporting interface for reviewers and statisticians.

**Features:**
- Coarse (TSAC×SOSAC, 11×16 = 176 scenarios) and fine (21×21 = 441 scenarios) grids
- Per-scenario Gini coefficient, Spearman ρ vs pure IUSAF, band-order preservation, TSAC/IUSAF ratios
- Balance-point identification (Gini-minimum subject to structural constraints)
- Integrity checks export (`integrity_checks.csv`)
- Markdown summary generation
- Named balance-point scenarios: `iusaf_pure`, `iusaf_strict`, `gini_minimum`, `band_order_boundary`

## Balance Point Scenarios (v4.0)

The v4.0 methodology replaces the arbitrary Spearman ρ ≥ 0.85 threshold with **band-order preservation** (Band 5 mean > Band 6 mean) plus a Spearman safety floor of 0.80. Four named scenarios at SOSAC=3%:

| Scenario | TSAC (β) | SOSAC (γ) | Description |
|----------|----------|-----------|-------------|
| IUSAF (Pure) | 0.0% | 3% | Pure inverted UN Scale — no terrestrial stewardship overlay |
| Strict | 1.5% | 3% | Conservative stewardship overlay; band order fully preserved |
| Gini-minimum | 2.5% | 3% | Lowest Gini preserving band order (Spearman ρ ≈ 0.945) |
| Band-order boundary | 3.0% | 3% | Band 6 mean equals Band 5 mean — structural limit of band-order preservation |

→ Full stewardship design: [reference/methodology.md](reference/methodology.md)

## Data Sources

| Source | Purpose |
|--------|---------|
| UN Scale of Assessments (2025–2027) | Assessed budget shares per Party |
| CBD COP16 Budget Table | Source of truth for 196 CBD Parties |
| UNSD M49 | Region, sub-region classifications |
| World Bank Income Classification | Income group labels |
| World Bank Land Area (FAOSTAT) | Terrestrial stewardship weights |

→ Full data pipeline: [reference/data-sources.md](reference/data-sources.md)

## Testing

```bash
# Run full test suite (178+ tests)
pytest tests/ -v

# Run IPLC structural validation (40 tests)
pytest iplc-developed/test_structural_validation.py -v

# Run with coverage
pytest tests/ --cov=src/cali_model --cov-report=term-missing
```

→ Full test catalog: [reference/validation.md](reference/validation.md)

## Branch Structure

| Branch | Status | Description |
|--------|--------|-------------|
| `main` | Active | Production code, 178+ tests, app.py + sensitivity.py |
| `terrestrial` | Parked | Banded TSAC variant (banded_app.py), calibration harness, v4.2 sensitivity reports |

Archived/deleted branches: `iplc` (merged to main), `optiond` (merged to main as v4.0).

## IPLC Developed-Country Analysis

The `iplc-developed/` directory contains a paper-exercise calculating IPLC allocations for 9 developed countries (Australia, Canada, Denmark, Finland, Japan, New Zealand, Norway, Russia, Sweden) under two hypothetical scenarios:

- **Option 1**: Raw equality for all Parties, filtered to the 9 countries (IPLC ≈ 2.30% of fund).
- **Option 2**: Banded IUSAF with the 9 countries added to Bands 4–5 (IPLC ≈ 2.11% of fund).

The closeness of these results is structurally expected: Band 4 countries gain relative to equality while Band 5 countries lose, and the effects partially cancel. See [iplc-developed/validation_analysis.md](iplc-developed/validation_analysis.md).

## Version History

See [change_log.md](change_log.md) for the full versioned history. Key milestones:

- **v3**: 6-band IUSAF, Gini reporting, balance-point analysis, 138 tests
- **v4.0**: Band-order preservation replaces Spearman 0.85 threshold, gini_optimal → gini_minimum rename
- **v4.1**: Balance-point ranking tables, IPLC developed-country tables, DuckDB fix
- **v4.2**: Banded TSAC app, calibration harness, v4 sensitivity reports (terrestrial branch)
- **v4.2.1**: DuckDB StringDtype fix on main, IPLC structural validation (40 tests)

## Use of AI

The code base is written in Python using [Factory AI Droid](https://factory.ai/) as the development harness. 
- Current main coding model: GLM-5 (Z.ai). 
- High-level reasoning through Opus 4.6–4.7, GPT-5.4-5.5 Codex. 
- Code planning and automated peer review uses GPT-5 Codex, Claude Opus 4.6-4.7, and Gemini Pro 3. The main models used to write code were GPT5 Codex (various) and Claude Sonnet switching to GLM-5.1 - the Droid default - for v4 for its robustness. 
- Code and model review sessions were performed outside of Droid in independent clean sessions in Claude Code (Anthropic), Codex (Open AI) and Antigravity (Google). Model based peer review proved invaluable in identifying issues requiring attention prior to human review (such as catching that a Spearman value of 0.85 used during model exploration had become hard coded). But caution is required with higher level reasoning models such as the recent Opus 4.7 due to a tendency to produce irrelevant and confusing clutter. LLMs are an aid for improving critical human review: not a replacement for it. 
- The responsible human is Dr. Paul Oldham.
