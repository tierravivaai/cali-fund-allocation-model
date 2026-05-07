# Country Annexes

Per-country allocation tables for the four named balance-point scenarios at four fund sizes.

## Scenarios

| Scenario | TSAC (β) | SOSAC (γ) | Description |
|----------|----------|-----------|-------------|
| IUSAF (Pure) | 0.0% | 3% | Pure inverted UN Scale — no terrestrial stewardship overlay |
| Strict | 1.5% | 3% | Conservative stewardship overlay; band order fully preserved |
| Gini-minimum | 2.5% | 3% | Lowest Gini preserving band order (Spearman ρ ≈ 0.945) |
| Band-order boundary | 3.0% | 3% | Band 6 mean equals Band 5 mean — structural limit |

## Fund Sizes

$50M, $200M, $500M, $1B (IPLC share fixed at 50%).

## Structure

```
country-annexes/
├── generate_all_fund_sizes.py       # Generates all annexes (4 scenarios × 4 fund sizes)
├── combine_annexes.py               # Merges 4 scenario DOCX into 1 combined DOCX per fund size
├── fifty-million/
│   ├── iusaf-pure/iusaf-pure-country-annex.{csv,docx,md}
│   ├── iusaf-strict/...
│   ├── gini-minimum/...
│   ├── band-order-boundary/...
│   └── country-annexes-fifty-million.docx    # Combined annex
├── two-hundred-million/...
├── five-hundred-million/...
└── one-billion/...
```

Each scenario subdirectory contains three formats:
- **CSV** — machine-readable allocation data
- **MD** — markdown table for review
- **DOCX** — formatted Word document for distribution

Combined annexes (one per fund size) merge all four scenarios into a single DOCX.

## Regeneration

```bash
python country-annexes/generate_all_fund_sizes.py
python country-annexes/combine_annexes.py
```
