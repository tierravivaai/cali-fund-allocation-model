# Scripts

Standalone generation and validation scripts. These are not part of the core model (`src/cali_model/`) but produce output tables, Word documents, and validation reports used in the working paper and annexes.

## Table Generation

| Script | Purpose |
|--------|---------|
| `validate_all_tables.py` | Generates and validates all CSV tables against the live calculator; outputs to `model-tables/` and `model-tables/table-validation/` |
| `generate_optiond_tables.py` | Generates band-order preservation and breakpoint summary tables (DOCX + CSV) |
| `generate_balance_point_rankings.py` | Generates balance-point ranked country tables |
| `generate_tsac_section_draft.py` | Generates the TSAC section draft DOCX (tables E1, E2, A, B, C, D1, D2) |
| `rank_panels_scenarios.py` | Generates scenario comparison panels |
| `rank_change_scenarios.py` | Generates rank-change scenario tables |

## Country Annexes

| Script | Purpose |
|--------|---------|
| `generate_all_fund_sizes.py` | Generates country annexes for 4 scenarios × 4 fund sizes (see `country-annexes/`) |

## Calibration

| Script | Purpose |
|--------|---------|
| `calibrate_banded_tsac.py` | Calibration harness for banded TSAC weight configurations; outputs to `sensitivity-reports/v4-sensitivity-reports/calibration/` |

## Utilities

| Script | Purpose |
|--------|---------|
| `generate_party_master.py` | Generates `config/party_master.csv` override table |
| `cross_check_cbd.py` | Cross-checks CBD party list against UN scale data |
| `csv_to_word.py` | Converts CSV tables to formatted Word documents |
| `csv_to_word_lib.py` | Shared library for CSV→Word conversion |
| `md_to_word_rationale.py` | Converts markdown rationale documents to Word |
