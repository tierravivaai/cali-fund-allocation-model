# Unconstrained Gini Minimum Analysis

## Purpose

This analysis asks: if we relax the requirement that IUSAF band order be preserved, where does the Gini coefficient achieve its absolute minimum, and what are the consequences? This complements the band-preserving balance-point analysis already in the paper.

## Method

Using the same IUSAF allocation model (142 eligible Parties, fund = USD 1,000M, IPLC 50/50, SOSAC fixed at 3%), we sweep TSAC from 0% to 20% with band-inversion weighting and compute the Gini coefficient, Spearman rank correlation vs pure IUSAF, band-order preservation, and component decomposition at each point.

## Key Finding

| Setting | TSAC | SOSAC | IUSAF | Gini | Band Order | Band 5/6 Margin | Spearman ρ | Stewardship > IUSAF |
|---------|------|-------|-------|------|------------|-----------------|------------|-------|
| Pure IUSAF | 0% | 3% | 97% | 0.1011 | Preserved | +46.7% | 1.000 | No |
| Strict | 1.5% | 3% | 95.5% | 0.0933 | Preserved | +19.3% | 0.951 | No |
| **Gini-min (band-preserved)** | **2.5%** | **3%** | **94.5%** | **0.0886** | **Preserved** | **+5.4%** | **0.945** | **Yes (China)** |
| Band-order boundary | 3.0% | 3% | 94.0% | 0.0866 | Just violated | −0.6% | 0.929 | Yes (China) |
| **Unconstrained Gini minimum** | **5.35%** | **3%** | **91.65%** | **0.0828** | **Violated** | **−22.7%** | **0.839** | **Yes (China, Brazil)** |
| TSAC-dominated | 9.2% | 3% | 87.8% | 0.0877 | Violated | −45.7% | 0.696 | Yes (5 parties) |

The unconstrained Gini minimum of **0.0828** occurs at **TSAC = 5.35%**, an absolute reduction of only 0.006 from the band-preserving minimum (0.0886). On the 0–1 Gini scale this is a marginal improvement — small enough that a reader comparing 0.0886 and 0.0828 could reasonably consider them functionally equivalent for policy purposes. The often-cited "6.5% relative improvement" is misleading because it divides two already-small numbers (0.006 / 0.0886), inflating the apparent significance. In absolute terms the gain is negligible relative to the structural cost. At this point:

1. **Band order is severely inverted**: Band 6 (China) mean = $8.50M exceeds Band 5 mean = $6.93M by 22.7%.
2. **Spearman ρ drops to 0.839**, indicating a substantial departure from the IUSAF ranking.
3. **TSAC exceeds IUSAF for 2 parties** (China and Brazil), meaning the stewardship component dominates the equity base for the two largest-landmass Parties.

## Component Decomposition

At the unconstrained minimum (TSAC = 5.35%, SOSAC = 3%), the total budget is split:

| Component | Budget | Share | Concentration (top 5) |
|-----------|--------|-------|------------------------|
| IUSAF | $916.5M | 91.65% | 4.3% |
| TSAC | $53.5M | 5.35% | 33.4% |
| SOSAC | $30.0M | 3.00% | 12.8% |

IUSAF still provides 91.65% of the total budget. The Gini improvement comes not from TSAC being "in control" overall, but from TSAC's extreme concentration on a few large-landmass Parties acting as a local lever.

### Per-band component shares

| Band | n | Mean alloc | IUSAF % | TSAC % | SOSAC % | TSAC > IUSAF? |
|------|---|-----------|---------|--------|---------|-----------------|
| Band 1 (≤0.001%) | 31 | $8.38M | 93.3% | 0.3% | 6.4% | No |
| Band 2 (0.001–0.01%) | 59 | $7.20M | 94.4% | 3.7% | 1.9% | No |
| Band 3 (0.01–0.1%) | 30 | $6.11M | 94.1% | 4.3% | 1.6% | No |
| Band 4 (0.1–1.0%) | 18 | $5.72M | 87.1% | 11.4% | 1.5% | No |
| Band 5 (1.0–10.0%) | 3 | $6.93M | 60.3% | 39.7% | 0.0% | Brazil only |
| Band 6 (>10.0%) | 1 | $8.50M | 24.5% | 75.5% | 0.0% | China |

Only in Bands 5 and 6 does TSAC contribute a significant share of any Party's allocation. For the 128 Parties in Bands 1–4, IUSAF remains the dominant component (87–94%).

## Comparison: Band-preserving vs Unconstrained

| Aspect | Band-preserved (2.5%) | Unconstrained (5.35%) |
|--------|----------------------|----------------------|
| Gini coefficient | 0.0886 | 0.0828 |
| Gini improvement vs pure IUSAF (absolute) | 0.013 | 0.018 |
| Gini improvement vs pure IUSAF (relative) | 12.4% | 18.1% |
| Band order preserved? | Yes (5.4% margin) | No (−22.7%) |
| Spearman ρ | 0.945 | 0.839 |
| Parties where TSAC > IUSAF | 1 (China) | 2 (China, Brazil) |
| China: TSAC/IUSAF ratio | 1.40 | 3.08 |
| LDC total | 331.08M | 330.80M |
| SIDS total | 311.01M | 310.00M |
| Min-Party (Band 1) allocation | $8.83M | $8.58M |
| Max-Party (Band 5, Brazil) | $5.44M | $9.62M |

## Interpretation

The unconstrained Gini minimum is effectively a "land-area redistribution" scenario masked behind a veneer of IUSAF. Although IUSAF still provides 91.65% of the total budget, the 5.35% TSAC lever — concentrated on just two Parties (China receives 75.5% of its allocation from TSAC; Brazil 59.4%) — is sufficient to reorder the top of the distribution. The additional Gini reduction from relaxing band order is only 0.006 in absolute terms (from 0.0886 to 0.0828). While this is sometimes expressed as "6.5% relative improvement", that framing divides two already-small numbers and overstates the practical significance; on the 0–1 Gini scale, the difference between 0.0886 and 0.0828 is marginal.

The flatness of the Gini surface around the minimum (0.082834 at 5.35% vs 0.082891 at 5.0%) means the exact minimiser is a matter of numerical precision rather than policy significance. The Gini achieves near-minimal values across a 0.5 percentage-point window (TSAC 5.1–5.5%), all of which severely violate band order.

**Policy implication**: The band-preservation constraint is not merely a technical nicety — it enforces a structural property (no higher-numbered band exceeds a lower-numbered one) that is central to the IUSAF's political legitimacy. The unconstrained minimum achieves only a marginal additional Gini improvement (0.006 in absolute terms, from 0.0886 to 0.0828) at the cost of a severe structural violation and a large rank-order disruption (Spearman ρ drops from 0.945 to 0.839). The "6.5% relative improvement" framing should be read cautiously: it divides two small numbers and overstates the practical difference.

## Reproducibility

All outputs can be regenerated by running:

```bash
python3 band-analysis/gini-unconstrained/gini_unconstrained_analysis.py
```

This produces the following CSV files in `band-analysis/gini-unconstrained/`:

| File | Description |
|------|-------------|
| `gini-sweep.csv` | 25-row sweep of TSAC from 0% to 20% with Gini, Spearman, band metrics |
| `top-recipients.csv` | Top 30 recipient Parties at the unconstrained minimum |
| `component-breakdown.csv` | Per-band IUSAF/TSAC/SOSAC shares at TSAC=5.35% |
| `component-breakdown-band-preserved.csv` | Per-band shares at TSAC=2.5% for comparison |
| `component-concentration.csv` | Top-N concentration of IUSAF vs TSAC vs SOSAC |
| `balance-point-comparison.csv` | Side-by-side comparison of four balance points |
