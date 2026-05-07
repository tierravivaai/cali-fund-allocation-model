# src/

Application and model code for the Cali Fund Allocation Model.

## Applications

| File | Description |
|------|-------------|
| `app.py` | Main Streamlit negotiation app — interactive interface for exploring policy scenarios |
| `sensitivity.py` | Sensitivity & robustness app — parameter sweeps, balance-point analysis, reporting |

## Core Library

`cali_model/` contains the calculation engine:

| Module | Description |
|--------|-------------|
| `calculator.py` | `calculate_allocations()` — the core allocation function and aggregation helpers |
| `data_loader.py` | DuckDB-based ETL: raw CSV/XLSX → merged `base_df` |
| `balance_analysis.py` | Fine-grained sweeps, Gini-minimum identification, balance-point detection |
| `sensitivity_metrics.py` | Gini coefficient, Spearman ρ, component ratios, integrity checks |
| `sensitivity_scenarios.py` | Scenario definitions, one-way/two-way grids, neighbour generation |
| `reporting.py` | Markdown and CSV export generation for the sensitivity app |
