# TSAC × SOSAC Two-way Grid Analysis

## Context

One-way sweeps (v3) held one stewardship parameter fixed while varying the other; the two-way grid sweeps both simultaneously, revealing interaction effects that are otherwise invisible. This generalises the v3 sensitivity framework to the full TSAC × SOSAC parameter surface.

*This analysis addresses peer review recommendation 3.6 (MEDIUM).*

## Grid Design

- **Coarse grid**: TSAC β = 0–15% (1% steps, 16 values) × SOSAC γ = 0–10% (1% steps, 11 values) → 176 scenarios
- **Fine grid**: TSAC β = 0–10% (0.5% steps, 21 values) × SOSAC γ = 0–10% (0.5% steps, 21 values) → 441 scenarios
- **Baseline scenario**: Gini-minimum point (β=2.5%, γ=3%), band inversion, high-income excluded, IPLC 50%
- **Comparator**: Pure band-inversion IUSAF (β=0, γ=0) computed for each grid point

## Gini Coefficient Contours

The Gini coefficient ranges from 0.0723 to 0.1422 across the coarse grid.

**Global minimum** (fine grid): β=4.5%, γ=0.0%, Gini=0.0723

**Low-Gini zone** (Gini < 0.08, fine grid): 56 scenarios occupy a curved band from
β≈2.0% at γ=0% to β≈8.5% at γ≈2.0%.
This ridge does not follow a simple additive path — adding SOSAC shifts the
Gini-minimum TSAC level upward, confirming non-linear interaction.

Gini distribution across coarse grid:
- Gini < 0.08: 16 scenarios
- 0.08 ≤ Gini < 0.09: 28 scenarios
- 0.09 ≤ Gini < 0.10: 34 scenarios
- Gini ≥ 0.10: 98 scenarios

## Spearman Rank Correlation Contours

Spearman ρ vs pure IUSAF ranges from 0.39 to 1.00.

Overlay classification (coarse grid):
- Minimal overlay (ρ ≥ 0.95): 9 scenarios
- Moderate overlay (0.85 ≤ ρ < 0.95): 35 scenarios
- Dominant overlay (ρ < 0.85): 132 scenarios

The gini-minimum point (β=2.5%, γ=3%) falls in the moderate overlay zone with
Spearman ρ=0.85 — consistent with the v3 one-way sweep findings.

## TSAC/IUSAF Balance Threshold

The TSAC component first exceeds the IUSAF component for any Party at
β=2%, γ=0%.
Across the coarse grid, 154/176 scenarios
exceed this balance — the binding Party is China (Band 6, largest land area).

Maximum TSAC/IUSAF ratio: 10.6× at β=15%
, γ=10%.

## Cross-section: SOSAC Fixed at 3%

This is the one-way TSAC sweep from v3 (γ=3% held constant), now embedded in the
two-way grid. The Gini-minimum is at β=5% (Gini=0.0829), matching v3 results.

| β | Gini | Spearman ρ | SIDS total ($m) | LDC total ($m) |
|---|------|-----------|----------------|----------------|
| 0% | 0.1011 | 0.9771 | 325.5 | 335.1 |
| 1% | 0.0958 | 0.9521 | 322.6 | 334.3 |
| 2% | 0.0909 | 0.9477 | 319.7 | 333.5 |
| 3% | 0.0866 | 0.9290 | 316.8 | 332.7 |
| 4% | 0.0839 | 0.8977 | 313.9 | 331.9 |
| 5% | 0.0829 | 0.8520 | 311.0 | 331.1 |
| 6% | 0.0832 | 0.8083 | 308.1 | 330.3 |
| 7% | 0.0841 | 0.7864 | 305.2 | 329.5 |
| 8% | 0.0856 | 0.7429 | 302.3 | 328.7 |
| 9% | 0.0877 | 0.7127 | 299.4 | 327.9 |
| 10% | 0.0902 | 0.6662 | 296.5 | 327.1 |
| 11% | 0.0932 | 0.6196 | 293.6 | 326.3 |
| 12% | 0.0968 | 0.5752 | 290.7 | 325.5 |
| 13% | 0.1008 | 0.5377 | 287.8 | 324.7 |
| 14% | 0.1050 | 0.4990 | 284.9 | 323.9 |
| 15% | 0.1095 | 0.4726 | 282.0 | 323.1 |

## Cross-section: TSAC Fixed at 2.5%

This is the one-way SOSAC sweep from v3 (β=2.5% held constant), from the fine grid.

| γ | Gini | Spearman ρ | SIDS total ($m) | LDC total ($m) |
|---|------|-----------|----------------|----------------|
| 0% | 0.0763 | 0.9446 | 297.4 | 337.9 |
| 0.5% | 0.0779 | 0.9451 | 300.9 | 337.1 |
| 1% | 0.0798 | 0.9450 | 304.3 | 336.3 |
| 1.5% | 0.0819 | 0.9449 | 307.8 | 335.5 |
| 2% | 0.0841 | 0.9449 | 311.3 | 334.7 |
| 2.5% | 0.0863 | 0.9448 | 314.8 | 333.9 |
| 3% | 0.0886 | 0.9448 | 318.3 | 333.1 |
| 3.5% | 0.0909 | 0.9422 | 321.7 | 332.3 |
| 4% | 0.0933 | 0.9355 | 325.2 | 331.5 |
| 4.5% | 0.0959 | 0.9005 | 328.7 | 330.7 |
| 5% | 0.0987 | 0.8915 | 332.2 | 329.9 |
| 5.5% | 0.1016 | 0.8868 | 335.6 | 329.1 |
| 6% | 0.1045 | 0.8833 | 339.1 | 328.3 |
| 6.5% | 0.1075 | 0.8825 | 342.6 | 327.5 |
| 7.0% | 0.1104 | 0.8782 | 346.1 | 326.7 |
| 7.5% | 0.1135 | 0.8640 | 349.5 | 325.9 |
| 8% | 0.1166 | 0.8484 | 353.0 | 325.0 |
| 8.5% | 0.1198 | 0.8413 | 356.5 | 324.2 |
| 9% | 0.1230 | 0.8395 | 360.0 | 323.4 |
| 9.5% | 0.1262 | 0.8388 | 363.5 | 322.6 |
| 10% | 0.1294 | 0.8381 | 366.9 | 321.8 |

## Distributional Implications

SIDS totals range from $261.2m to $374.2m across the coarse grid.
LDC totals range from $311.9m to $339.9m.
Percentage of Parties below equality line: 35.2% to 67.6%.

Increasing SOSAC directly benefits SIDS countries (higher SIDS total).
Increasing TSAC primarily benefits large-land-area countries (China, Brazil, etc.).
The two effects compound non-linearly: high TSAC + high SOSAC reallocates from
IUSAF-driven recipients (typically small, low-income countries) toward both
large-land-area and SIDS countries simultaneously.

## Interaction Effects

The heatmaps reveal three distinct regions in the TSAC × SOSAC parameter space:

1. **IUSAF-dominated region** (low β, low γ): Shares closely follow pure IUSAF.
   Spearman ρ ≥ 0.95. Gini ~0.08–0.09. This is the minimal-overlay zone.

2. **Balanced-stewardship region** (moderate β and γ): The Gini-minimum ridge runs
   through this zone. Adding SOSAC shifts the Gini-optimal TSAC level upward.
   Spearman ρ 0.85–0.95. The v3 gini-optimal point (β=2.5%, γ=3%) sits here.

3. **Stewardship-dominated region** (high β or high γ): Large TSAC or SOSAC weights
   cause dominant overlay on IUSAF (Spearman ρ < 0.85). Distributional effects are
   driven primarily by the stewardship components rather than the equity base.

## Mechanical Validity

All 176 coarse-grid and 441 fine-grid scenarios satisfy conservation of shares
(sum = 1.0) and non-negativity. See integrity_checks.csv for detailed diagnostics.

## Relationship to V3 One-way Sweeps

The v3 TSAC sweep held γ=3% constant; the SOSAC sweep held β=2.5% constant.
These are single cross-sections through the two-way grid. The complete grid shows
that the gini-minimum point identified in v3 (β=5%, γ=3%) is a local minimum
along the γ=3% cross-section, but the global minimum on the two-way surface is at
β=4.5%, γ=0.0% (Gini=0.0723),
which lies on the γ=0% edge where SOSAC is absent.

This finding does not undermine the gini-optimal point as a policy choice —
it reflects the fact that adding SOSAC (which benefits SIDS countries) increases
Gini slightly, and the policy rationale for SOSAC is independent of Gini minimisation.

## Outputs

| File | Description |
|------|-------------|
| tsac_sosac_grid_coarse.csv | 176-row metrics table (1% steps) |
| tsac_sosac_grid_fine.csv | 441-row metrics table (0.5% steps) |
| tsac_sosac_heatmap_gini_coarse.png | Gini coefficient heatmap (coarse) |
| tsac_sosac_heatmap_spearman_coarse.png | Spearman ρ heatmap (coarse) |
| tsac_sosac_heatmap_gini_fine.png | Gini coefficient heatmap (fine) |
| tsac_sosac_heatmap_spearman_fine.png | Spearman ρ heatmap (fine) |

---
*Generated by scripts/generate_v4_md_reports.py*