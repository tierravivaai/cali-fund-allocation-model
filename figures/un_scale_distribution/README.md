# UN Scale of Assessment 2027 — Distribution Figures

Generated: 2026-04-15  
Project: Cali Allocation Model (Inverted UN Scale Option)  
Branch: `figures`

---

## Purpose

Illustrate the extreme skewness of the UN Scale of Assessment (2027) as the baseline data for the Cali Fund allocation model. The UN Scale is inverted to create the IUSAF weight (`1 / un_share_2027`), so understanding its distribution is essential.

---

## Figures

### Figure 1: Full Distribution — All Countries (Bar Chart)

| File | Format |
|------|--------|
| `fig_1_full_distribution.svg` | Vector |
| `fig_1_full_distribution.png` | Raster (200dpi) |
| `fig_1_full_distribution.csv` | Source data |

- **Source**: `data-raw/UNGA_scale_of_assessment.csv` (column: 2027)
- **Filter**: All 193 countries with non-zero UN share
- **Chart type**: Categorical bar chart with 5 percentage bands (0.001–0.01%, 0.01–0.1%, 0.1–1%, 1–10%, >10%)
- **Key stats**: Top 10 countries hold 72.3% of total shares

### Figure 2: CBD Parties — High Income Excluded, SIDS Preserved (Bar Chart)

| File | Format |
|------|--------|
| `fig_2_non_high_income.svg` | Vector |
| `fig_2_non_high_income.png` | Raster (200dpi) |
| `fig_2_non_high_income.csv` | Source data |

- **Source data**: UN Scale + CBD Parties list + WB Income Groups + SIDS flag
- **Filter**: CBD Parties, exclude High income except SIDS (`exclude_high_income=True, high_income_mode="exclude_except_sids"`)
- **N = 142** eligible Parties (3 with 0% UN share: State of Palestine, Cook Islands, Niue — all non-UN members)
- **Chart type**: Same 5 percentage bands as Fig 1
- **Key stats**: Top 10 countries hold 26.6% of total shares

### Figure 3: Two-Panel Ranked Bars — 142 Eligible Parties

| File | Format |
|------|--------|
| `fig_3_two_panel_ranked.svg` | Vector |
| `fig_3_two_panel_ranked.png` | Raster (200dpi) |

- **Layout**: Two vertical panels (portrait, 8×8 in)
  - Top panel: full range (0–20%) — shows China's dominance
  - Bottom panel: zoomed into 0–1.5% — reveals the long tail
- **Filter**: Same as Fig 2, EU excluded from display
- **No country names or text annotations inside figure**
- **Suitable for**: Word/LibreOffice documents (portrait orientation)

### Figure 4: Two-Panel Ranked Bars — Without Top Contributor

| File | Format |
|------|--------|
| `fig_4_two_panel_ranked_no_top.svg` | Vector |
| `fig_4_two_panel_ranked_no_top.png` | Raster (200dpi) |

- **Layout**: Same as Fig 3
  - Top panel: full range (0–1.5%) — China removed
  - Bottom panel: zoomed into 0–1.5%
- **Filter**: Same as Fig 2, excludes China (top contributor at 20.004%) and EU
- **N = 141** Parties
- **No country names or text annotations inside figure**

---

## Zero-Rated CBD Parties

Three CBD Parties have 0% on the UN Scale of Assessment because they are not UN member states:

| Party | Reason | WB Income Group | SIDS | CBD Budget Share |
|-------|--------|----------------|------|-----------------|
| State of Palestine | UN non-member observer state | Lower middle income | No | 0.014% |
| Cook Islands | Free association with NZ | High income | Yes | 0.001% |
| Niue | Free association with NZ | High income | Yes | 0.001% |

The European Union is also a CBD Party with 0% UN share but is excluded from the 142 eligible Parties (High income, not SIDS).

---

## Data Pipeline

All figures use the model's own `cali_model.data_loader` pipeline (`load_data()` + `get_base_data()`) to ensure consistent Party lists, name mapping, income classification, and SIDS flags. This guarantees the figures match exactly what the calculator produces.

---

## Regeneration

```bash
# From project root, with virtual environment active
python figures/un_scale_distribution/generate_plots.py
```

Outputs all SVG, PNG, and CSV files to this directory. README.md timestamps update automatically.

---

## Implementation Notes

- `plot_distribution()`: Categorical bar chart with percentage bands (Figs 1–2)
- `plot_ranked_bars()`: Single wide panel, ranked individual bars (kept for reference but not committed)
- `plot_ranked_bars_two_panel()`: Two-panel portrait layout with zoom (Figs 3–4)
- The zoom y-max (1.5%) was chosen to capture the top ~15 parties below China while keeping the long tail visible
- PNG export at 200dpi for Word document insertion; SVG for publication-quality editing
