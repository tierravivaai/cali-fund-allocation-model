# Band Weight Flattening and Optimal Weights

## The Question

The IUSAF allocates biodiversity fund shares using six bands, each with a weight that determines the per-country allocation. Under the current weights [1.50, 1.30, 1.10, 0.95, 0.75, 0.40], a Band 1 country (the smallest UN contributors, predominantly LDCs and SIDS) receives 3.75 times what China (Band 6) receives. This "staircase" pattern — where each band is noticeably different from its neighbours — produces a Gini coefficient of 0.087.

Two natural questions arise:

1. **Can the weights be flattened to reduce inequality while preserving the principle that the poorest receive more than the largest contributors?**
2. **Is there an optimal set of weights that minimises inequality subject to a meaningful policy constraint?**

The answer to both is yes, and the results are striking.

## Band Composition

The 142 eligible Parties under the current IUSAF ($1 billion fund, high-income excluded except SIDS, pure IUSAF with beta = 0, gamma = 0) distribute across bands as follows:

| Band | UN Scale | n | LDC | SIDS | WB Income Mix | Mean Allocation |
|------|----------|---|-----|------|---------------|-----------------|
| Band 1 | ≤ 0.001% | 31 | 13 | 22 | 7 low, 10 lower-mid, 9 upper-mid, 5 hi | $8.53M |
| Band 2 | 0.001–0.01% | 59 | 31 | 11 | 19 low, 23 lower-mid, 14 upper-mid, 3 hi | $7.39M |
| Band 3 | 0.01–0.1% | 30 | 0 | 4 | 12 lower-mid, 15 upper-mid, 3 hi | $6.25M |
| Band 4 | 0.1–1.0% | 18 | 0 | 2 | 5 lower-mid, 12 upper-mid, 1 hi | $5.40M |
| Band 5 | 1.0–10.0% | 3 | 0 | 0 | 1 lower-mid (India), 2 upper-mid (Brazil, Mexico) | $4.26M |
| Band 6 | > 10.0% | 1 | 0 | 0 | 1 upper-mid (China) | $2.27M |

Key facts:
- 88% of Parties (120 of 142) are in Bands 1–4
- All 44 LDC Parties are in Band 1 (13) or Band 2 (31)
- All 39 SIDS Parties are in Band 1 (22), Band 2 (11), Band 3 (4), or Band 4 (2)
- Band 5 contains India (lower-middle income) plus Brazil and Mexico (upper-middle income)
- Band 6 contains only China (upper-middle income)

## Finding 1: Monotonicity Is Trivially Satisfied

Because every country within a band receives the same weight, the per-band mean allocation is proportional to the weight itself. Monotonic band order (Band 1 mean > Band 2 mean > ... > Band 6 mean) therefore requires only that w1 > w2 > w3 > w4 > w5 > w6 > 0.

**Any strictly decreasing weight sequence preserves monotonicity.** This means the constraint places almost no restriction on how far weights can be compressed. The policy question is not "what spread preserves band order?" (answer: any), but "what differentiation is appropriate?"

## Finding 2: The Current Staircase Is Far from Optimal

The current weights create a uniform staircase where each band has a noticeably different weight from its neighbours. This is not the only way to achieve a B1/B6 ratio of 3.75. Consider two weight profiles, both satisfying B1/B6 ≥ 3.75:

| | Current (staircase) | Optimal (front-loaded) |
|---|---|---|
| w1 | 1.50 | 1.46 |
| w2 | 1.30 | 1.45 |
| w3 | 1.10 | 1.39 |
| w4 | 0.95 | 1.23 |
| w5 | 0.75 | 0.91 |
| w6 | 0.40 | 0.39 |
| **Gini** | **0.0873** | **0.0352** |
| B1 mean | $8.53M | $7.38M |
| B4 mean | $5.40M | $6.22M |
| B6 mean | $2.27M | $1.97M |
| LDC total | $339.9M | $323.3M |

**Same B1/B6 ratio, 60% lower Gini.** The optimal profile keeps w1 and w6 almost identical but compresses Bands 1–4 from a steep staircase to a gentle ramp. Since 88% of Parties are in Bands 1–4, reducing variance within this majority block dramatically lowers inequality.

The current staircase allocates $8.53M to Band 1 and only $5.40M to Band 4 — a 1.58:1 ratio among developing countries that sits adjacent in the UN scale. The optimal profile narrows this to $7.38M vs. $6.22M (1.19:1), making allocations between LDCs and upper-middle-income developing countries much more equitable while maintaining the same floor-vs-ceiling differential.

## Finding 3: The Efficient Frontier

The question "what is the optimal set of weights?" is parameterised by a policy choice: the minimum B1/B6 ratio. This ratio represents "how many times more should the poorest countries receive than the largest contributor?" For each floor ratio R, we solve:

> Minimise Gini(w1, ..., w6) subject to w1/w6 ≥ R and w1 > w2 > w3 > w4 > w5 > w6 > 0

The result is an efficient frontier — for each level of differentiation, the lowest achievable Gini:

| B1/B6 Floor | Optimal Gini | Optimal Weights | B1 mean | B4 mean | B5 mean | B6 mean | LDC total | SIDS total |
|-------------|-------------|-----------------|---------|---------|---------|---------|-----------|------------|
| 1.00× | 0 (equality) | [1.00, 1.00, 1.00, 1.00, 1.00, 1.00] | $7.04M | $7.04M | $7.04M | $7.04M | $310M | $275M |
| 1.50× | 0.016 | [0.92, 0.91, 0.90, 0.85, 0.76, 0.61] | $7.22M | $6.67M | $5.97M | $4.79M | $315M | $279M |
| 2.00× | 0.023 | [1.80, 1.79, 1.74, 1.61, 1.34, 0.90] | $7.27M | $6.50M | $5.41M | $3.64M | $319M | $281M |
| 2.50× | 0.029 | [1.80, 1.79, 1.73, 1.57, 1.25, 0.72] | $7.31M | $6.37M | $5.07M | $2.93M | $321M | $282M |
| 3.00× | 0.032 | [0.90, 0.90, 0.86, 0.77, 0.59, 0.30] | $7.35M | $6.29M | $4.84M | $2.45M | $322M | $283M |
| 3.75× | 0.035 | [1.46, 1.45, 1.39, 1.23, 0.91, 0.39] | $7.38M | $6.22M | $4.61M | $1.97M | $323M | $284M |
| — | 0.087 | [1.50, 1.30, 1.10, 0.95, 0.75, 0.40] | $8.53M | $5.40M | $4.26M | $2.27M | $340M | $305M |

The last row is the **current** staircase weights — it sits well above the frontier, showing that the current weights achieve the right B1/B6 differential but with a sub-optimal interior shape.

(All dollar amounts verified against the full IUSAF calculator, $1 billion fund, 142 eligible Parties. LDC and SIDS totals are exact from the calculator output.)

## The Shape Effect

The shape of the interior weights matters as much as the B1/B6 endpoints. Three shapes at the same B1/B6 ≈ 2.0× ratio illustrate this:

| Shape | Weights | Gini | B1 mean | B6 mean |
|-------|---------|------|---------|---------|
| Linear interpolation | [1.265 → 0.682] (spread 0.58) | 0.0509 | $7.91M | $4.26M |
| Front-compressed | [1.186 → 0.637] (spread 0.55) | 0.0401 | $7.70M | $4.13M |
| Back-compressed | [1.185 → 0.638] (spread 0.55) | 0.0400 | $7.69M | $4.14M |

Both front- and back-compressed shapes achieve the same B1/B6 ratio with ~21% lower Gini than the linear interpolation. The key is that compressing the interior bands (where most Parties sit) reduces within-majority variance regardless of whether the compression comes from the top or the bottom.

The constrained optimisation goes further: by searching over the full 6-dimensional weight space, it finds shapes that front-load the differentiation even more aggressively (w1 ≈ w2 ≈ w3), achieving Gini = 0.023 at the 2.0× floor — 55% lower than the linear path at the same ratio.

## Fairness for Middle-Income Countries

A central concern is fairness: the IUSAF should direct more resources to the least developed countries, but it should also be fair to larger middle-income developing countries that are themselves biodiversity-rich.

Under the current staircase weights:
- Band 1 (LDCs, small islands): **$8.53M** per country
- Band 4 (e.g. South Africa, Argentina, Thailand): **$5.40M** per country
- Band 5 (Brazil, India, Mexico): **$4.26M** per country
- Band 6 (China): **$2.27M** per country

The 1.58:1 ratio between Band 1 and Band 4 means upper-middle-income developing countries receive only 63% of what LDCs receive — a large gap between countries that are all eligible for the fund.

Under the optimal weights at the 2.0× floor:
- Band 1: **$7.27M** per country
- Band 4: **$6.50M** per country
- Band 5: **$5.41M** per country
- Band 6: **$3.64M** per country

The Band 1/Band 4 ratio narrows to 1.12:1, while still maintaining the principle that the poorest receive the most. Brazil, India, and Mexico each receive $5.41M — 27% more than the current $4.26M — and China receives $3.64M instead of $2.27M (a 60% increase).

The trade-off is that Band 1 countries receive somewhat less ($7.27M vs $8.53M, a 15% reduction), and the LDC aggregate total drops from $340M to $319M. Whether this trade-off is acceptable depends on the policy priority: is it more important to maximise the LDC share, or to ensure that all developing countries receive allocations that reflect their standing as Parties to the Convention?

## Comparison with Other Equalisation Levers

The IUSAF has two other mechanisms for reducing inequality:

1. **TSAC blending (adding a land-area component):** The unconstrained Gini minimum at TSAC = 5.35% achieves Gini = 0.083 — a reduction of only 0.004 from the pure IUSAF baseline of 0.087. This comes at the cost of severe band-order inversion and a Spearman rank correlation drop to 0.839.

2. **Weight flattening (reducing band weight spread):** The optimal weights at the same 3.75× floor achieve Gini = 0.035 — a reduction of 0.052, an order of magnitude larger than TSAC can achieve. And it does so with **no** band-order violation, because the optimal shape is still strictly decreasing.

| Lever | Gini reduction | Band order preserved | Rank correlation |
|-------|---------------|---------------------|-----------------|
| TSAC 5.35% (unconstrained) | 0.004 | No (−22.7% inversion) | ρ = 0.839 |
| Weight shape optimisation (3.75× floor) | 0.052 | Yes | ρ ≈ 1.0 |
| Weight shape + 2.0× floor | 0.064 | Yes | ρ ≈ 1.0 |

Weight flattening is both more powerful and less disruptive than TSAC blending. The two levers could also be combined — optimal weights at a lower floor ratio plus a modest TSAC share — though the incremental gain from TSAC on top of already-optimised weights would be negligible.

## The Policy Choice

The analysis reframes the design question from "what weight spread should we use?" to "what minimum differentiation floor is appropriate?" The efficient frontier shows the trade-off:

- **1.0×: Full equality** — zero Gini, but every country receives the same regardless of contribution level. The inversion principle is purely nominal.
- **1.5×: Moderate differentiation** — Gini = 0.016, Band 1 receives 50% more than China. Upper-middle-income developing countries receive 93% of what LDCs receive.
- **2.0×: Standard differentiation** — Gini = 0.023, Band 1 receives double China. A clear but moderate inversion signal. Upper-middle-income developing countries receive 89% of what LDCs receive.
- **3.75×: Current IUSAF level** — Gini = 0.035 (optimal) or 0.087 (current staircase). Band 1 receives 3.75× China. The inversion signal is strong, but creates a 1.58:1 gradient within the developing-country majority.

At any floor ratio, the optimal shape always front-loads the differentiation: Bands 1–3 receive nearly equal weights, with the required B1/B6 ratio achieved primarily through reduced weights for Bands 5 and 6. This is because optimising Gini means reducing variance where most parties sit (88% are in Bands 1–4), not spreading it evenly across all bands.

## Reproducibility

All results can be replicated using the scripts in `band-analysis/band-weights-flatten/`:

```bash
# Linear interpolation sweep (named profiles + spread sweep)
python3 band-analysis/band-weights-flatten/band_weights_flatten_analysis.py

# Optimal weights with B1/B6 floor constraint
python3 band-analysis/band-weights-flatten/optimal_weights_constrained.py

# Linear-interpolation floor sweep (for comparison)
python3 band-analysis/band-weights-flatten/optimal_weights_analysis.py
```

Data files produced:
- `efficient-frontier.csv` — the efficient frontier (24 B1/B6 floors)
- `optimal-weights.csv` — full weight vectors at each frontier point
- `optimal-allocations.csv` — per-band allocation detail at each frontier point
- `weight-profiles.csv` — named profiles along the linear interpolation path
- `gini-vs-spread.csv` — Gini as a function of weight spread
- `weight-shape-comparison.csv` — linear vs front-compressed vs back-compressed shapes
