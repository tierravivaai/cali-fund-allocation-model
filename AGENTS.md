# AGENTS

## Data Locations
- Source inputs: `data-raw/`
- Outputs: `data/`

## Structure
- SQL model: `model/allocation.sql`
- Scripts: `scripts/`
- Tests: `tests/`

## Commands
```bash
python scripts/run_duckdb.py --db cali_fund.duckdb
pytest
```
