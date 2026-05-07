# Tests

Pytest test suite (138 tests) covering mathematical integrity, UI behaviour, and data consistency.

## Running

```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/cali_model --cov-report=term-missing
```

## Test Modules

| Module | Focus |
|--------|-------|
| `test_logic.py` | Party count, inversion logic, allocation sums, metadata |
| `test_band_inversion.py` | Band assignment, weight normalisation, mode consistency |
| `test_tsac_sosac.py` | Component blending, isolation, SIDS preservation |
| `test_totals.py` | Aggregation (region, income, LDC, SIDS) |
| `test_floor_ceiling.py` | Constraint redistribution |
| `test_equality_mode.py` | Equal shares, mode switching |
| `test_tiny_scenarios.py` | Fund conservation at extreme sizes |
| `test_negotiator_dashboard.py` | Baseline comparison |
| `test_ui_reset.py` | Preset buttons, reset defaults |
| `test_ui_columns.py` | Tab content, column ordering |
| `test_ui_selectors.py` | Region/sub-region filtering |
| `test_stewardship_warnings.py` | Blend threshold triggers |
| `test_sensitivity_modules.py` | Gini, Spearman, balance-point metrics |
| `test_balance_analysis.py` | Fine sweeps, Gini-minimum identification |
| `test_sensitivity_metrics.py` | Integrity checks |
| `test_reporting.py` | Markdown/CSV export integrity |
| `test_app_dataframes.py` | Streamlit dataframe export regression |
| `test_aggregates.py` | EU block, special group aggregation |
| `test_dashboard_stability.py` | Negotiation dashboard rendering |
| `test_income_tabs.py` | Income group tab totals |
| `test_income_validation.py` | Income classification correctness |
| `test_eligibility.py` | Eligibility filtering |
| `test_formatting.py` | Currency display |

See [reference/validation.md](../../reference/validation.md) for full test catalogue.
