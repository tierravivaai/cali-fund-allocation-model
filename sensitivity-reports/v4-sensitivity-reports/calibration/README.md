# Calibration

Outputs from the banded TSAC calibration harness (`scripts/calibrate_banded_tsac.py`). Each row in the grid is a two-way TSAC×SOSAC sweep (176 scenarios) for one band-weight configuration.

## Configurations

| Name | Description |
|------|-------------|
| `linear_baseline` | Linear TSAC (current default) |
| `linear_progression` | Linear progression band weights |
| `geometric_base_1.5` | Geometric band weights (base 1.5) |
| `geometric_base_2` | Geometric band weights (base 2) — recommended preset |
| `geometric_base_3` | Geometric band weights (base 3) |
| `capped_top` | Capped top-band weights |
| `flat` | Flat/equal band weights |

## Files Per Configuration

- `*_grid.csv` — 176-scenario grid with metrics per row
- `*_integrity.csv` — Integrity check results per scenario

## Summary Files

| File | Description |
|------|-------------|
| `calibration_results.csv` | Aggregate comparison across configurations |
| `calibration_summary.md` | Narrative summary of calibration findings |
| `all_integrity_checks.csv` | Combined integrity checks across all configurations |
| `calibration_comparison.png` | Visual comparison of configurations |
| `calib_gini_min_value.png` | Gini-minimum value by configuration |
| `calib_max_tsac_iusaf_ratio.png` | Max TSAC/IUSAF ratio by configuration |
| `calib_moderate_overlay_count.png` | Moderate overlay scenario count by configuration |

## Regeneration

```bash
python scripts/calibrate_banded_tsac.py
```
