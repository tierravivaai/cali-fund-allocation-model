# Band Weight Flattening Analysis

## Purpose

This analysis investigates what happens to IUSAF allocations when we flatten the band weights while preserving monotonic band order. The IUSAF uses six bands with weights [1.50, 1.30, 1.10, 0.95, 0.75, 0.40] — a 3.75:1 ratio from the smallest to the largest contributor. This analysis asks: if we compress those weights toward equality, how much does inequality between Parties change, and at what point does the "band inversion" principle become meaningless?

## Key Finding

**The monotonicity constraint is trivially satisfied.** Because every country within a band receives the same weight, per-band mean allocation is proportional to the weight itself. Monotonicity therefore requires only w1 > w2 > ... > w6 > 0 — any strictly decreasing sequence preserves it. This means the constraint provides almost no restriction on how far weights can be compressed.

**The Gini coefficient is highly sensitive to weight spread.** As weights flatten, Gini drops sharply:

| Profile | Weights | Spread | B1/B6 Ratio | Gini | Monotonic |
|---------|---------|--------|-------------|------|-----------|
| Current | 1.50 → 0.40 | 1.10 | 3.75x | 0.0873 | Yes |
| Moderate | 1.25 → 0.75 | 0.50 | 1.67x | 0.0509 | Yes |
| Flat-linear | 1.20 → 0.80 | 0.40 | 1.50x | 0.0416 | Yes |
| Near-flat | 1.10 → 0.90 | 0.20 | 1.22x | 0.0217 | Yes |
| Minimal | 1.05 → 0.95 | 0.10 | 1.11x | 0.0111 | Yes |
| Equality | 1.00 → 1.00 | 0.00 | 1.00x | 0.0000 | No* |

*Equality fails strict monotonicity because all bands have equal mean allocation (7.042M), not because any band exceeds a lower-numbered one.

The relationship between weight spread and Gini is approximately linear in the range [0.2, 1.1], meaning each 0.01 reduction in spread reduces Gini by roughly 0.00077. The Gini is essentially determined by the spread, not by the specific weight shape.

## Scenario Parameters

- 142 eligible Parties (high-income excluded, except SIDS)
- Fund: USD 1,000M (1 billion)
- IPLC: 50/50 state split
- Pure IUSAF: beta = 0, gamma = 0 (no TSAC, no SOSAC)
- UN scale mode: band_inversion

## Per-Band Allocation Comparison

| Band | n | Current (1.50/0.40) | Moderate (1.25/0.75) | Near-flat (1.10/0.90) | Equality (1.00) |
|------|---|---------------------|----------------------|----------------------|-----------------|
| Band 1 (≤0.001%) | 31 | $8.53M | $7.89M | $7.40M | $7.04M |
| Band 2 (0.001–0.01%) | 59 | $7.39M | $7.26M | $7.13M | $7.04M |
| Band 3 (0.01–0.1%) | 30 | $6.25M | $6.62M | $6.86M | $7.04M |
| Band 4 (0.1–1.0%) | 18 | $5.40M | $5.99M | $6.59M | $7.04M |
| Band 5 (1.0–10.0%) | 3 | $4.26M | $5.36M | $6.33M | $7.04M |
| Band 6 (>10.0%) | 1 | $2.27M | $4.73M | $6.06M | $7.04M |
| **Gini** | | **0.0873** | **0.0509** | **0.0217** | **0.0000** |

The table shows that flattening from current weights to near-flat (1.10/0.90) roughly triples China's allocation (from $2.27M to $6.06M) while reducing Band 1 allocations by only $1.13M. The redistribution is progressive in the sense that the largest gains go to the smallest number of Parties in the highest bands.

## Gini vs Weight Spread

The fine sweep (51 points from spread=1.10 to spread≈0) shows an approximately linear relationship:

- At spread = 1.10 (current): Gini = 0.0873
- At spread = 0.50: Gini ≈ 0.0483
- At spread = 0.20 (near-flat): Gini ≈ 0.0207
- At spread = 0.10 (minimal): Gini ≈ 0.0106
- At spread = 0.00 (equality): Gini = 0.0000

The slope is approximately 0.079 per unit of spread — meaning reducing the weight spread by 0.10 reduces Gini by roughly 0.008. This is substantially larger than the TSAC lever effect (the entire TSAC range from 0% to 5% moves Gini from 0.087 to 0.083, a change of 0.004 for a 5-percentage-point shift).

## Policy Implications

1. **Weight flattening is a much more powerful equaliser than TSAC.** Moving from current weights to near-flat (1.10/0.90) reduces Gini by 0.066 — roughly 16 times the effect of adding TSAC at the Gini-minimum (0.006). The sensitivity of Gini to weight spread dwarfs the sensitivity to the TSAC blend parameter.

2. **The current weight spread of 1.10 is a policy choice, not a mathematical requirement.** Monotonicity is preserved for any strictly decreasing weight sequence. The spread could be 0.40, 0.20, or 0.10 with no structural violation. The question is not "what spread preserves band order?" (answer: any), but "what spread is appropriate for the policy goals?"

3. **The Gini at near-flat weights (0.022) is already below what TSAC blending can achieve at any blend level.** Even at the unconstrained Gini minimum (TSAC = 5.35%), the Gini is 0.083 — four times higher than near-flat weights without any TSAC at all.

4. **The trade-off is between redistribution and the inversion principle's expressivity.** At near-flat weights (1.10/0.90), Band 1 parties receive only 1.22× what Band 6 receives. The inversion still holds, but the "signal" of differentiated need based on contribution level is greatly attenuated. Whether this is desirable is a policy question, not a technical one.

5. **Band 6 (China) weight floor.** The current weight of 0.40 gives China $2.27M. At 0.80 (flat-linear), China receives $5.15M. At 0.90 (near-flat), China receives $6.06M. These are within the defensible range noted in the band configuration (0.30–0.55), but the analysis shows that even at 0.55, the monotonicity constraint is fully satisfied for all five other bands.

## Comparison with TSAC Blending

| Lever | Parameter range | Gini range | Maximum Gini improvement |
|-------|-----------------|------------|--------------------------|
| TSAC blending (β) | 0% – 5% | 0.087 – 0.083 | 0.004 (absolute) |
| Band weight flattening (spread) | 1.10 – 0.00 | 0.087 – 0.000 | 0.087 (absolute) |

Weight flattening is an order of magnitude more powerful than TSAC blending as an equalisation mechanism. The two levers operate on different principles: TSAC adds a land-area component that concentrates resources on a few large-territory Parties, while weight flattening reduces the differentiation between IUSAF bands.

## Reproducibility

All outputs can be regenerated by running:

```bash
python3 band-analysis/band-weights-flatten/band_weights_flatten_analysis.py
```

This produces the following CSV files in `band-analysis/band-weights-flatten/`:

| File | Description |
|------|-------------|
| `weight-profiles.csv` | 6 named profiles + 19 parametric sweeps with Gini and band metrics |
| `allocation-by-band.csv` | Per-band mean and total allocation for each profile (150 rows) |
| `gini-vs-spread.csv` | Fine-grained sweep: Gini as a function of weight spread (51 points) |
| `extreme-profiles.csv` | Detailed stats at the 5 key named profiles |

## Optimal Weights Analysis: Minimising Gini by Floor Ratio

The flattening analysis above uses a single weight family (linear interpolation from current to equality). But the weight **shape** also matters — the same B1/B6 ratio can be achieved with very different interior weights, and some shapes produce much lower Gini.

### The shape discovery

Running a constrained optimisation (minimise Gini subject to B1/B6 >= R) reveals that the **optimal shape front-loads the differentiation**: Bands 1–3 receive nearly equal weights, with the B1/B6 ratio achieved primarily by reducing w5 and w6. This is because 88% of eligible Parties (120 of 142) are in Bands 1–4, and reducing the variance within this majority block dramatically lowers Gini.

**Current weights at B1/B6 = 3.75: [1.50, 1.30, 1.10, 0.95, 0.75, 0.40] → Gini = 0.087**

**Optimal weights at B1/B6 = 3.75: [1.46, 1.45, 1.39, 1.23, 0.91, 0.39] → Gini = 0.035**

Same ratio, 60% lower Gini. The optimal keeps B1 and B6 almost unchanged (1.46 vs 1.50, 0.39 vs 0.40) but compresses the interior from a steep staircase to a gentle ramp.

### Efficient frontier

| B1/B6 Floor | Optimal Gini | vs Current Gini (0.087) | Weights (w1...w6) | B1 mean | B6 mean | LDC total | SIDS total |
|-------------|-------------|--------------------------|-------------------|---------|---------|-----------|------------|
| 1.00× | 0 (equality) | −100% | [1.00, 1.00, 1.00, 1.00, 1.00, 1.00] | $7.04M | $7.04M | $310M | $275M |
| 1.25× | 0.009 | −89% | [0.45, 0.45, 0.44, 0.43, 0.40, 0.36] | $7.13M | $5.70M | $313M | $277M |
| 1.50× | 0.016 | −82% | [0.92, 0.91, 0.90, 0.85, 0.76, 0.61] | $7.19M | $4.79M | $316M | $279M |
| 1.75× | 0.020 | −77% | [1.26, 1.26, 1.23, 1.14, 0.98, 0.72] | $7.23M | $4.13M | $318M | $280M |
| 2.00× | 0.024 | −73% | [1.80, 1.79, 1.74, 1.61, 1.34, 0.90] | $7.27M | $3.63M | $319M | $281M |
| 2.50× | 0.029 | −67% | [1.80, 1.79, 1.73, 1.57, 1.25, 0.72] | $7.31M | $2.93M | $321M | $282M |
| 3.00× | 0.032 | −63% | [0.90, 0.90, 0.86, 0.77, 0.59, 0.30] | $7.35M | $2.45M | $322M | $283M |
| 3.75× | 0.035 | −60% | [1.46, 1.45, 1.39, 1.23, 0.91, 0.39] | $7.38M | $1.97M | $323M | $284M |

*(Note: LDC and SIDS totals are approximate, computed from per-band means and LDC/SIDS counts per band. For exact totals, the full calculator must be run.)*

### The policy question reframed

The analysis reframes the question from "what weight spread is appropriate?" to "what minimum differentiation floor (B1/B6 ratio) is appropriate?" Given any floor R, there exists an optimal weight shape that minimises Gini while guaranteeing Band 1 countries receive at least R times what Band 6 receives.

The key trade-offs:

- **At R = 1.5× (LDCs get 50% more than China):** Gini = 0.016 — near-equality between developing countries. China receives $4.79M vs $7.19M for Band 1 LDCs. Brazil/India/Mexico receive $5.96M (between Band 1 and Band 6).
- **At R = 2.0× (LDCs get double China):** Gini = 0.024 — moderate differentiation. China receives $3.63M, Band 1 receives $7.27M. Brazil/India/Mexico receive $5.41M.
- **At R = 3.75× (current IUSAF level):** Gini = 0.035 (optimal) or 0.087 (current) — either way Band 1 receives 3.75× what China receives.

The difference between "optimal at 3.75×" (Gini = 0.035) and "current at 3.75×" (Gini = 0.087) shows that **the current weights achieve the right B1/B6 ratio but with a sub-optimal interior shape**. Compressing Bands 1–4 from a steep staircase (1.50, 1.30, 1.10, 0.95) to a gentle ramp (1.46, 1.45, 1.39, 1.23) reduces Gini by 60% while leaving the B1/B6 differential unchanged.

### Why the current weights are sub-optimal

The current weights create a **staircase** pattern where each band is noticeably different from its neighbours. Because 88% of parties are in Bands 1–4, this staircase creates significant inequality within the majority. The optimal shape **front-loads** the differentiation: nearly-equal weights for Bands 1–3, a modest step at Band 4, and the large differential compressed into Bands 5–6. This reduces within-majority variance while preserving the between-floor differential.

### Fairness for middle-income countries

At the current weights:
- Band 1 (LDCs, small islands): $8.53M per country
- Band 4 (upper-middle income like South Africa, Argentina): $5.40M per country
- Band 5 (Brazil, India, Mexico): $4.26M per country
- Band 6 (China): $2.27M per country

At the current weights, there is a 3.75:1 ratio between Band 1 and Band 6, but also a large gap between Band 1 and Band 4 (1.58:1). The optimal at R=2.0× provides:
- Band 1: $7.27M
- Band 4: $6.49M
- Band 5: $5.41M
- Band 6: $3.63M

The Band 1/Band 4 ratio drops from 1.58 to 1.12, making allocations between LDCs and upper-middle-income developing countries much more equitable, while still maintaining the principle that the poorest receive the most.

## Relationship to Other Analyses

- **`gini-unconstrained/`**: Investigates what happens when TSAC is added to IUSAF (varying beta). Found that the unconstrained Gini minimum (0.0828) offers only 0.006 improvement over the band-preserved minimum (0.0886). By contrast, weight optimisation at the same B1/B6 floor achieves 0.035 — an order of magnitude larger improvement.
- **`stewardship-pool/`**: Restructures the stewardship pool tables (TSAC + SOSAC) for clarity, with deterministic component splits.
- **This analysis**: Investigates two related questions: (1) what happens when band weights are flattened along the current staircase path, and (2) what is the optimal weight shape at each B1/B6 floor? The latter reveals that the current staircase is far from optimal — front-loading the differentiation into the B5/B6 gap while compressing B1–B3 achieves 60% lower Gini at the same differentiation floor.

## Reproducibility

All outputs can be regenerated by running:

```bash
# Flattening analysis (linear interpolation)
python3 band-analysis/band-weights-flatten/band_weights_flatten_analysis.py

# Constrained optimisation (optimal weight shape at each floor)
python3 band-analysis/band-weights-flatten/optimal_weights_constrained.py
```

This produces the following CSV files in `band-analysis/band-weights-flatten/`:

| File | Description |
|------|-------------|
| `weight-profiles.csv` | 6 named profiles + 19 parametric sweeps with Gini and band metrics |
| `allocation-by-band.csv` | Per-band mean and total allocation for each profile (150 rows) |
| `gini-vs-spread.csv` | Fine-grained sweep: Gini as a function of weight spread (51 points) |
| `extreme-profiles.csv` | Detailed stats at the 5 key named profiles |
| `optimal-sweep.csv` | 201-point sweep: Gini and B1/B6 ratio along the linear interpolation path |
| `optimal-profiles.csv` | Key floor ratios along the linear path |
| `optimal-profiles-detail.csv` | Per-band allocation detail at key floor ratios |
| `weight-shape-comparison.csv` | Linear vs front-compressed vs back-compressed weight shapes |
| `efficient-frontier.csv` | 24-point efficient frontier: optimal Gini at each B1/B6 floor |
| `optimal-weights.csv` | Full weight vectors at each point on the frontier |
| `optimal-allocations.csv` | Per-band allocation detail at each frontier point |
