# Cali Fund Allocation Model

## Overview
Parameterised allocation model using DuckDB and SQL. Source inputs are in `data-raw/` and outputs are written to `data/`.

## Inputs
Required CSVs in `data-raw/`:
- `cbd_cop16_budget_table.csv`
- `unsd_region_useme.csv`
- `eu27.csv`
- Optional: `manual_name_map.csv`

## Run
```bash
python scripts/run_duckdb.py --db cali_fund.duckdb
```

## Tests
```bash
pytest
```
