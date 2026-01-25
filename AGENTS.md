# AGENTS

## Data Locations
- Source inputs: `data-raw/`
- Outputs: `data/`

## Structure
- Dashboard: `dashboard.py` (Streamlit implementation of the 6-phase journey)
- SQL model: `model/allocation.sql` (Core allocation logic)
- Public/internal views: `model/public_internal.sql`
- Scripts: `scripts/run_duckdb.py` (Database build and export)
- Tests: `tests/`
- Archive: `archive/` (Old documentation and specs)

## Commands
```bash
./start_dashboard.sh
/Users/pauloldham/Documents/cali-allocation-model/.venv/bin/python scripts/run_duckdb.py --db cali_fund.duckdb
/Users/pauloldham/Documents/cali-allocation-model/.venv/bin/python -m pytest
```
