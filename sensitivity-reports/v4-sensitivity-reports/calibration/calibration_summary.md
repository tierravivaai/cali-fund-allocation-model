# Banded TSAC Calibration Summary

## Headline Metrics by Configuration

| Config | Gini-min (β, γ) | Gini | Max TSAC/IUSAF | Crossing β | Overlay ≥ 0.85 | Criteria 1 | Criteria 2 | Criteria 3 | All pass |
|--------|------------------|------|-----------------|------------|-----------------|------------|------------|------------|----------|
| geometric_base_2 | (14%, 0%) | 0.064689 | 1.40× | 12% | 122/176 | PASS | PASS | PASS | PASS |

## Acceptance Criteria

1. **Primary**: TSAC/IUSAF ratio ≤ 2.0 across entire grid
2. **Secondary**: Moderate-overlay zone (ρ ≥ 0.85) ≥ 35/176 scenarios
3. **Tertiary**: Gini-minimum ≤ 0.0723 (current linear TSAC value)

## Top-10 TSAC Shares at Gini-minimum

### geometric_base_2

| Party | TSAC Share |
|-------|-----------|
| Algeria | 1.5936% |
| Libya | 1.5936% |
| Sudan | 1.5936% |
| Ethiopia | 1.5936% |
| Angola | 1.5936% |
| Chad | 1.5936% |
| Democratic Republic of the Congo | 1.5936% |
| South Africa | 1.5936% |
| Mali | 1.5936% |
| Mauritania | 1.5936% |

## Recommendation

No recommendation is made. The selection of band-weight configuration is a group
decision for the methodological review process.

## Integrity Checks

All sampled scenarios pass integrity checks for all configurations. See
`calibration/<config>_integrity.csv` for details.