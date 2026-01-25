# AGENTS

## Data Locations
- Source inputs: `data-raw/`
- Outputs: `data/`

## Structure
- SQL model: `model/allocation.sql`
- Public/internal views: `model/public_internal.sql`
- Scripts: `scripts/`
- Tests: `tests/`

## Commands
```bash
/Users/pauloldham/Documents/cali-allocation-model/.venv/bin/python scripts/run_duckdb.py --db cali_fund.duckdb
/Users/pauloldham/Documents/cali-allocation-model/.venv/bin/python -m pytest
```
