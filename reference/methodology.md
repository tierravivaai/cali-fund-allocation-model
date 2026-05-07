# Methodology and Stewardship Design

## Allocation Formula

**Final Share = (1 − β − γ) × IUSAF + β × TSAC + γ × SOSAC**

Where:
- **IUSAF** (Inverted UN Scale Allocation Function): the equity base, tilted towards lower-income and least developed countries.
- **TSAC** (Terrestrial Stewardship Allocation Component): adjustment for land-area-based stewardship.
- **SOSAC** (SIDS Ocean Stewardship Allocation Component): equal-share pool for eligible SIDS.
- **β** (TSAC weight) and **γ** (SOSAC weight) are user-adjustable sliders.
- The IPLC/State split divides each Party's allocation at the selected percentage (default 50/50).

## IUSAF: Raw Inversion vs Band-Based Inversion

### Raw Inversion
Each eligible Party's UN assessed share is inverted (1/share) and normalised. This is the raw sovereign-capacity baseline.

### Band-Based Inversion (default)
Parties are grouped into 6 UN-share bands with pre-assigned weights, reducing sensitivity to very small share differences while preserving inverted-capacity logic.

| Band | UN Share Range | Weight |
|------|---------------|--------|
| Band 1 | ≤ 0.001% | 1.00 |
| Band 2 | 0.001% – 0.01% | 0.90 |
| Band 3 | 0.01% – 0.1% | 0.85 |
| Band 4 | 0.1% – 1.0% | 0.95 |
| Band 5 | 1.0% – 10.0% | 0.75 |
| Band 6 | > 10.0% | 0.40 |

Configuration: `config/un_scale_bands.yaml`.

## Balance Point Scenarios (v4.0)

The model identifies four named balance-point scenarios. All four hold SOSAC fixed at 3% and vary TSAC to explore the trade-off between the equity base and terrestrial stewardship:

| Scenario | TSAC (β) | SOSAC (γ) | Description |
|----------|----------|-----------|-------------|
| IUSAF (Pure) | 0.0% | 3% | Pure inverted UN Scale with band inversion — no terrestrial stewardship overlay |
| Strict | 1.5% | 3% | Conservative stewardship overlay; band order fully preserved |
| Gini-minimum | 2.5% | 3% | Minimises Gini coefficient subject to band-order preservation (Band 5 mean > Band 6 mean) and Spearman ρ ≥ 0.80 |
| Band-order boundary | 3.0% | 3% | The boundary at which Band 6 mean allocation equals Band 5 mean — the structural limit of band-order preservation |

**Band-order preservation** replaces the earlier arbitrary Spearman ρ ≥ 0.85 threshold. The empirical structural break is at TSAC ≈ 3.0% (Spearman ρ ≈ 0.93), where Band 6 mean allocation catches up with Band 5. Country annex tables for all four scenarios are generated at four fund sizes ($50M, $200M, $500M, $1B) and are available under `country-annexes/`.

## Stewardship Slider Design

- **Defaults**: TSAC 0.00, SOSAC 0.00 (true equality start).
- **Gini-minimum preset**: TSAC 2.5%, SOSAC 3%.
- **Ranges**: TSAC 0–15%; SOSAC 0–10%; step 1%.
- **Blend warnings**: mild at β+γ > 0.15; strong at β+γ > 0.20; hard stop at β+γ ≥ 1.0.

## Floor and Ceiling

Floor and ceiling constraints are provided as optional modelling controls. They are **not active by default**.

- **Floor**: Sets minimum share per eligible country. Maximum feasible floor = 100 / n_eligible. Funds are redistributed proportionally.
- **Ceiling**: Sets maximum share per eligible country. Surplus is redistributed proportionally.
- **Both enabled**: Countries below floor are lifted up; countries above ceiling are reduced; remaining funds redistributed. Total always sums to fund size.

These are illustrative parameters for exploring distributional outcomes, not policy commitments.
