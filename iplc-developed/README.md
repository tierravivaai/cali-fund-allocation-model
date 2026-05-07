# IPLC Developed-Country Analysis

Calculation of IPLC allocations for 9 developed countries under two hypothetical scenarios, as a paper exercise for the working paper.

## Countries

Australia, Canada, Denmark, Finland, Japan, New Zealand, Norway, Russia, Sweden

## Scenarios

- **Option 1 (Raw Equality):** All Parties receive equal shares, filtered to the 9 countries. IPLC ≈ 2.30% of fund.
- **Option 2 (Banded IUSAF):** The 9 countries are added to IUSAF bands (Band 4: Denmark, Finland, NZ, Norway, Sweden; Band 5: Australia, Canada, Japan, Russia) with `exclude_hi` overridden only for these 9. IPLC ≈ 2.11% of fund.

The closeness is structurally expected: Band 4 countries gain relative to equality while Band 5 countries lose, and the effects partially cancel.

## Files

| File | Description |
|------|-------------|
| `specification.md` | Option 1 & 2 specification |
| `iplc-option1-equality.md` | Option 1 analysis and results |
| `iplc-option1-equality-*.csv` | Option 1 per-fund-size CSVs ($50M, $200M, $500M, $1B) + summaries |
| `iplc-option2-banded.md` | Option 2 analysis and results |
| `iplc-option2-banded-*.csv` | Option 2 per-fund-size CSVs + summaries |
| `test_structural_validation.py` | 40 structural validation tests (8 invariants × 2 options × fund sizes) |
| `validation_analysis.md` | Why Option 1 ≈ Option 2 |

## Running Tests

```bash
pytest iplc-developed/test_structural_validation.py -v
```
