# Data Raw

Source data files used as inputs to the DuckDB ETL pipeline (`src/cali_model/data_loader.py`).

## Files

| File | Source | Purpose |
|------|--------|---------|
| `UNGA_scale_of_assessment.csv` | UN General Assembly | Assessed budget shares per Party (2025–2027) |
| `cbd_cop16_budget_table.csv` | CBD COP16 | Source of truth for 196 CBD Party list |
| `un_classifications.csv` | UNSD M49 | Region, sub-region, intermediate region |
| `world_bank_income_class.csv` | World Bank | Income group labels (Low, Lower-middle, Upper-middle, High) |
| `CLASS_2025_10_07.xlsx` | World Bank | Income classification source spreadsheet |
| `eu27.csv` | EU | EU membership flags |
| `manual_name_map.csv` | Manual | Cross-references UN, World Bank, and CBD Party names |
| `countrycode.csv` | ISO | Country code concordance |
| `country_overlay.csv` | Derived | Country overlay flags |
| `unsd_region_useme.csv` | UNSD | Region classification (alternative source) |
| `API_AG.LND.TOTL.K2_DS2_en_csv_v2_749.zip` | World Bank/FAOSTAT | Land area in km² (compressed) |
| `API_AG.LND.TOTL.K2_DS2_en_csv_v2_749/` | World Bank/FAOSTAT | Land area CSV + metadata (extracted) |

## Documentation

- `README_WORLD_BANK_CLASS_2025_10_07` — notes on the World Bank income classification file
- `README-LAND-.API_AG.LND.TOTL.K2_DS2.txt` — notes on the land area API download

## Pipeline

All files are loaded by `src/cali_model/data_loader.py` which creates DuckDB tables and produces a merged `base_df` (197 rows × 27 columns). See [reference/data-sources.md](../reference/data-sources.md) for the full pipeline description.
