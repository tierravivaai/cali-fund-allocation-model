# Config

Model configuration files.

| File | Purpose |
|------|---------|
| `un_scale_bands.yaml` | 6-band UN Scale weight configuration (band ranges and weights) |
| `party_master.csv` | Single auditable source of truth for name concordance and data overrides (60 entries: income groups, regions, LDC/SIDS flags, EU membership, land area) |

## Band Configuration

The 6-band structure in `un_scale_bands.yaml`:

| Band | UN Share Range | Weight |
|------|---------------|--------|
| Band 1 | ≤ 0.001% | 1.00 |
| Band 2 | 0.001% – 0.01% | 0.90 |
| Band 3 | 0.01% – 0.1% | 0.85 |
| Band 4 | 0.1% – 1.0% | 0.95 |
| Band 5 | 1.0% – 10.0% | 0.75 |
| Band 6 | > 10.0% | 0.40 |

Loaded by `src/cali_model/data_loader.py` via `load_band_config()`.

## Party Master

`party_master.csv` contains override columns (`income_group_override`, `region_override`, `is_ldc_override`, `is_sids_override`, `is_eu_ms_override`, `land_area_km2_override`, `wb_land_area_name`) applied via `COALESCE` in the DuckDB SQL query. Each override row includes a `reason` column for auditability. See `scripts/generate_party_master.py` for generation.
