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
/Users/pauloldham/Documents/cali-allocation-model/.venv/bin/python scripts/run_duckdb.py --db cali_fund.duckdb
```

## Outputs
Written to `data/`:
- `allocation_country.csv`
- `allocation_country_internal.csv`
- `allocation_country_public.csv`
- `un_region.csv`
- `un_subregion.csv`
- `allocation_un_intermediate_region.csv`
- `allocation_eu.csv`
- `allocation_eu_total.csv`
- `allocation_devstatus.csv`

## Tests
```bash
/Users/pauloldham/Documents/cali-allocation-model/.venv/bin/python -m pytest
```
