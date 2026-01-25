# Cali Fund Allocation Model

## Overview
Parameterised allocation model using DuckDB and SQL. This project features an **Educational Journey Dashboard** that guides users through the allocation logic in 6 phases.

## Dashboard
The dashboard uses Streamlit to visualize the impact of various moderation mechanisms (Smoothing, Lower Bounds, Caps, and Baseline Blends).

Run the dashboard:
```bash
./start_dashboard.sh
```

## Data Inputs
Required CSVs in `data-raw/`:
- `cbd_cop16_budget_table.csv`
- `unsd_region_useme.csv`
- `eu27.csv`
- Optional: `manual_name_map.csv`

## Model Execution
Run the model directly to update the DuckDB database and export CSVs:
```bash
/Users/pauloldham/Documents/cali-allocation-model/.venv/bin/python scripts/run_duckdb.py --db cali_fund.duckdb
```

## Outputs
Written to `data/`:
- `allocation_country.csv`
- `allocation_country_internal.csv`
- `allocation_country_public.csv`

## Tests
```bash
/Users/pauloldham/Documents/cali-allocation-model/.venv/bin/python -m pytest
```
