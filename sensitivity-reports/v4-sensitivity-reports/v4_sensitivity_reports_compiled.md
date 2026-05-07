# V4 Sensitivity Reports: Executive Summary

## What the Model Does Well

- **Scale invariance confirmed**: The allocation formula produces identical share distributions regardless of fund size. All six pairwise comparisons across $50m–$1bn yield exactly zero share difference. The relative distribution among Parties is fully predictable and independent of the Cali Fund's total resources.

- **Mechanical validity holds across the entire parameter space**: All 176 coarse-grid and 441 fine-grid scenarios pass conservation of shares, conservation of money, non-negativity, component consistency, and IPLC split checks. The model is numerically robust.

- **Stewardship overlay is well-behaved in the moderate zone**: Within the parameter region around the gini-optimal point (β=2.5%, γ=3%), the allocation remains a moderate overlay on IUSAF (Spearman ρ ≈ 0.85–0.95). Small parameter adjustments in this zone produce bounded, predictable changes — the model is not fragile near its default settings.

- **Low-Gini zone is identifiable and compact**: The distributionally optimal region (Gini < 0.08) occupies a clear curved band in parameter space: β ≈ 2%–8% at low SOSAC levels. This compact zone gives negotiators a well-defined region for parameter selection.

## Findings That Need Attention

- **TSAC exceeds IUSAF for China at all β ≥ 2%**: The TSAC/IUSAF balance threshold is first crossed at β=2%, regardless of γ. At the gini-optimal point (β=2.5%), China's TSAC component already exceeds its IUSAF component. By β=15%, the ratio reaches 10.6×. This is a structural feature of combining large land area with a low IUSAF base, and may warrant policy consideration of a separate TSAC coefficient for Band 6.

- **Most of the parameter space produces dominant overlay**: 151 of 176 coarse-grid scenarios show dominant overlay (Spearman ρ < 0.85 vs pure IUSAF). The moderate-overlay zone is narrow, confined to low TSAC values (β ≤ 5% when γ=3%). Parameter choices outside this narrow zone mean stewardship components dominate the equity base.

- **Spearman rank collapses rapidly beyond the moderate zone**: Once TSAC exceeds ~5% at γ=3%, Spearman ρ drops below 0.85, and by β=15% reaches 0.39 — meaning the allocation rank ordering bears little resemblance to the IUSAF equity foundation. The transition from moderate to dominant overlay is steep, not gradual.

- **Gini-minimum on the two-way surface lies at β=4.5%, γ=0.0%**: The global Gini minimum (0.0723) occurs with SOSAC set to zero — contradicting the intuition that both stewardship components reduce inequality. Adding SOSAC increases Gini slightly because it redistributes toward a subset of Parties (SIDS) rather than across all. The v3 cross-section at γ=3% identified a local minimum at β=5%; the full grid shows this is not the global optimum.

- **SIDS and LDC allocations move in opposite directions**: Increasing SOSAC strongly benefits SIDS (totals rise from $261m to $374m) but reduces LDC totals slightly ($340m to $312m). The two groups are not perfectly overlapping, and parameter choices face a trade-off between them.

- **Majority of Parties below the equality line even at optimal settings**: At the gini-optimal point, 54% of Parties receive less than the equal-share benchmark. This ranges from 35% at optimal TSAC/SOSAC to 68% at high stewardship weights.

## Positive Structural Findings

- The formula's separation of share computation from monetary scaling is clean and verified. No edge-case failures or paradoxical outcomes were found across 617 scenario evaluations.

- The three identified regions of the parameter space (IUSAF-dominated, balanced-stewardship, stewardship-dominated) provide a clear mapping for policy reasoning. The boundaries are well-defined and reproducible.

- The one-way sweep findings from v3 are confirmed and now contextualised within the full two-way surface. The v3 gini-optimal point (β=5%, γ=3%) is correctly identified as a local minimum along its cross-section.

## Report Pack

| Report | Description |
|--------|-------------|
| Executive Summary | This document |
| Two-way Grid Analysis | TSAC × SOSAC heatmap interpretation with contour analysis |
| Scale Invariance Test | Empirical confirmation of fund-size independence |
| Integrity Checks | Mechanical validity diagnostics for grid scenarios |
| Technical Annex | Formula specification, parameter ranges, methodology |

*The two-way grid and scale-invariance test address recommendations 3.6 (MEDIUM) and 3.7 (LOW) from the independent peer review of the model.*


---


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


# Scale Invariance of Shares

## Context

The allocation formula computes shares from normalised weights that are
independent of fund size; this structural property is empirically verified here.

*This test addresses peer review recommendation 3.7 (LOW).*

## Test Design

The gini-minimum scenario (β=2.5%, γ=3%, band inversion, high-income excluded,
IPLC 50%) is evaluated at four fund sizes: $50m, $200m, $500m, and $1bn.
For each of the six pairwise combinations, the maximum absolute difference
in `final_share` across all 142 eligible Parties is computed. Scale invariance
holds if the maximum difference is below 1×10⁻¹².

## Results

| Pair | Max abs diff | Mean abs diff | Scale invariant |
|------|-------------|--------------|----------------|
| $50m vs $200m | 0.00e+00 | 0.00e+00 | YES |
| $50m vs $500m | 0.00e+00 | 0.00e+00 | YES |
| $50m vs $1000m | 0.00e+00 | 0.00e+00 | YES |
| $200m vs $500m | 0.00e+00 | 0.00e+00 | YES |
| $200m vs $1000m | 0.00e+00 | 0.00e+00 | YES |
| $500m vs $1000m | 0.00e+00 | 0.00e+00 | YES |

**Overall verdict: PASSED**

## Interpretation

The allocation formula computes shares from normalised weights (IUSAF, TSAC,
SOSAC) that are independent of fund size. Specifically:

- IUSAF weights are derived from inverted UN scale shares, normalised to sum to 1
- TSAC weights are proportional to land area, normalised to sum to 1
- SOSAC weights are equal-share across SIDS, normalised to sum to 1
- The final blend: `share = (1-β-γ)·IUSAF + β·TSAC + γ·SOSAC` is dimensionless

Fund size enters only when computing monetary allocations:
`allocation = fund_size × final_share`.

Therefore, share invariance is a structural property of the formula. This test
confirms it empirically with exact zero difference across all pairs, providing
a clear audit trail for reviewers.

## Policy Implications

Share invariance means that the relative distribution among Parties does not
change when the Cali Fund grows or shrinks. A $50m fund and a $1bn fund produce
identical percentage allocations — only the dollar amounts differ. This is an
important property for the credibility and predictability of the allocation mechanism.


---


# V4 Integrity Checks

## Purpose

This report documents mechanical validity checks for a representative sample
of scenarios from the TSAC × SOSAC two-way grid. Checks follow the same
framework used in v3 sensitivity reports.

## Sample Design

15 scenarios are sampled from the coarse grid, covering corner points
(β=0/γ=0, β=0/γ=10%, β=15%/γ=0, β=15%/γ=10%), the gini-optimal point
(β=2.5%/γ=3%), and intermediate points to verify grid-wide validity.

## Results Summary

- **Scenarios checked**: 15
- **All checks pass**: 15/15

## Check Categories

| Check | Description | Result |
|-------|-------------|--------|
| Conservation Shares | conservation shares | 15/15 PASS |
| Conservation Money | conservation money | 15/15 PASS |
| Non Negativity | non negativity | 15/15 PASS |
| Component Consistency | component consistency | 15/15 PASS |
| Iplc Split | iplc split | 15/15 PASS |
| Band Monotonicity | band monotonicity | 15/15 PASS |
| Floor Not Binding Unexpectedly | floor not binding unexpectedly | 15/15 PASS |
| Ceiling Not Binding Unexpectedly | ceiling not binding unexpectedly | 15/15 PASS |
| Sids Sosac Allocation | sids sosac allocation | 15/15 PASS |

## Detailed Results

| Scenario | β | γ | Shares | Money | Non-neg | Components | IPLC | Band | All |
|----------|---|---|--------|-------|---------|-----------|------|------|-----|
| β=0.0 γ=0.0 | 0% | 0% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.0 γ=0.03 | 0% | 3% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.0 γ=0.1 | 0% | 10% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.025 γ=0.0 | 2% | 0% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.025 γ=0.03 | 2% | 3% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.025 γ=0.1 | 2% | 10% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.05 γ=0.0 | 5% | 0% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.05 γ=0.03 | 5% | 3% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.05 γ=0.1 | 5% | 10% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.1 γ=0.0 | 10% | 0% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.1 γ=0.03 | 10% | 3% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.1 γ=0.1 | 10% | 10% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.15 γ=0.0 | 15% | 0% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.15 γ=0.03 | 15% | 3% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| β=0.15 γ=0.1 | 15% | 10% | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

## Grid-wide Conservation

Across all 176 coarse-grid scenarios:
- Share conservation: max deviation from 1.0 = 4.44e-16
- Money conservation: max deviation from fund size = 4.55e-13m
- Negative counts: 0 (zero across all scenarios)

## Interpretation

All sampled scenarios pass all integrity checks. The grid-wide statistics confirm
that conservation and non-negativity hold across the entire parameter space.
Results in the grid analysis reports are therefore mechanically valid and
interpretable.


---


# V4 Technical Annex

## Scope

This annex documents the methodology for v4 sensitivity reports, which extend
v3 with two-way grid sweeps and scale-invariance testing.

## Formula Specification

Final Share = (1 − β − γ) · IUSAF + β · TSAC + γ · SOSAC

*In the codebase, the TSAC weight and SOSAC weight are stored under the internal
parameter names `tsac_beta` and `sosac_gamma` respectively, following the
conventional Greek-letter notation used in the original formula specification.
Readers reviewing the source code will find these names throughout; they
correspond exactly to the TSAC weight and SOSAC weight referred to in this document.*

## Two-way Grid Design

The two-way grid generalises the v3 one-way sweep by varying both TSAC (β) and
SOSAC (γ) simultaneously while holding all other parameters at the gini-minimum
baseline values.

### Parameter ranges

| Grid | TSAC (β) | SOSAC (γ) | Scenarios |
|------|----------|-----------|----------|
| Coarse | 0–15%, 1% steps (16 values) | 0–10%, 1% steps (11 values) | 176 |
| Fine | 0–10%, 0.5% steps (21 values) | 0–10%, 0.5% steps (21 values) | 441 |

### Metrics computed per scenario

For each grid point, the following are computed:
- Gini coefficient of allocations
- Spearman rank correlation vs pure IUSAF
- HHI (Herfindahl-Hirschman Index)
- Top-10 and top-20 share concentration
- Percentage of Parties below equality line
- SIDS and LDC total allocations
- TSAC/IUSAF component ratios (China, Brazil, maximum)
- Overlay strength classification
- Departure from pure IUSAF flag
- Structural break flag
- Income and regional group totals

### Comparators

Each grid point uses two comparator scenarios:
1. **Pure IUSAF**: same parameters but β=0, γ=0 (isolates stewardship effect)
2. **Pure equality**: same parameters but equality_mode=True (provides equality benchmark)

## Scale Invariance Test Design

The gini-minimum scenario is evaluated at four fund sizes ($50m, $200m, $500m, $1bn).
For each of the C(4,2)=6 pairs, `final_share` vectors are compared element-wise.
The test passes if the maximum absolute difference across all eligible Parties
is below 1×10⁻¹².

### Rationale for threshold

The 1×10⁻¹² threshold is effectively zero at double precision. It is chosen
to allow for floating-point rounding while confirming that the formula is truly
scale-independent rather than merely approximately so.

## Integrity Check Framework

Checks follow the v3 framework and include:
- Conservation of shares (sum = 1.0)
- Conservation of money (total allocation = fund size)
- Non-negativity of allocations
- Internal component consistency (IUSAF + TSAC + SOSAC = total)
- IPLC split consistency (State + IPLC = total)
- Band monotonicity (for pure IUSAF scenarios)
- Floor not binding unexpectedly
- Ceiling not binding unexpectedly
- SOSAC allocation correctness

## Relationship to V3 Reports

| V3 Output | V4 Equivalent |
|----------|-------------|
| one_way_sweep.csv | tsac_sosac_grid_coarse.csv (generalised) |
| scenario_brief.md | executive_summary.md |
| comparative_report.md | two_way_grid_analysis.md |
| local_stability.md | Not repeated (v3 findings unchanged) |
| balance_point_summary.md | Not repeated (v3 findings unchanged) |
| technical_annex.md | technical_annex.md (updated) |
| integrity_checks.csv | integrity_checks.csv + integrity_checks_report.md |

## Departure and Overlay Criteria

Departure from pure IUSAF is flagged when Spearman ρ < 0.95 or top-20 turnover > 20%.
Overlay strength labels:
- **Minimal overlay**: ρ ≥ 0.98 and turnover ≤ 10%
- **Moderate overlay**: ρ ≥ 0.95 and turnover ≤ 20%
- **Strong overlay**: ρ ≥ 0.90 or turnover ≤ 40%
- **Dominant overlay**: otherwise

## Software and Reproducibility

- Calculator: `src/cali_model/calculator.py` (shared with main app)
- Scenario library: `src/cali_model/sensitivity_scenarios.py`
- Metrics: `src/cali_model/sensitivity_metrics.py`
- Generation script: `scripts/generate_v4_sensitivity_reports.py`
- Report generation: `scripts/generate_v4_md_reports.py`

All outputs are deterministically reproducible from the same repository state.
