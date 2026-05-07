# cali_model/

Core calculation library for the IUSAF allocation model. All allocation logic, data loading, sensitivity analysis, and reporting code lives here.

## Modules

| Module | Key Functions | Description |
|--------|---------------|-------------|
| `calculator.py` | `calculate_allocations()`, `assign_tsac_band()`, `banded_tsac_weights()` | Main allocation engine: IUSAF inversion, TSAC/SOSAC blending, floor/ceiling, IPLC split |
| `data_loader.py` | `load_data()`, `get_base_data()`, `load_band_config()` | DuckDB ETL pipeline: loads raw CSV/XLSX, joins tables, applies party_master overrides |
| `balance_analysis.py` | `run_fine_sweep()`, `identify_balance_points()`, `compute_gini()` | Fine-grained parameter sweeps, Gini-minimum identification, balance-point detection |
| `sensitivity_metrics.py` | `compute_metrics()`, `compute_component_ratios()`, `run_invariant_checks()` | Gini, Spearman, overlay strength, integrity checks, local stability |
| `sensitivity_scenarios.py` | `one_way_sweep()`, `two_way_grid()`, `get_scenario_library()` | Scenario definitions, sweep generation, neighbour scenarios |
| `reporting.py` | `generate_scenario_brief()`, `generate_sweep_summary()`, `generate_technical_annex()` | Markdown and CSV export generation for the sensitivity app |

## Design Notes

- **Naming convention**: `tsac_beta` and `sosac_gamma` are the internal code names for the user-facing TSAC and SOSAC weights. Display labels use "TSAC weight" and "SOSAC weight".
- **Backward compatibility**: `calculate_allocations()` defaults to `tsac_mode="linear"` preserving the original linear TSAC. The `"banded"` mode (geometric_base_2) is available via the `terrestrial` branch.
- **Data flow**: `data_loader.py` → `base_df` → `calculator.py` → `results_df` → app / sensitivity app
