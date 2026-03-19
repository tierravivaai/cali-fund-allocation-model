# Session Context: TSAC + SOSAC and Negotiation Dashboard

## Changes Implemented

### Data Ingestion
- Integrated World Bank land area data into the master Party table in `logic/data_loader.py`.
- Handled missing land area data for specific parties (Monaco, Cook Islands, Niue, State of Palestine).

### Core Logic
- Implemented a blended allocation formula in `logic/calculator.py`:
  `Final Share = (1 - beta - gamma) * iusaf_share + beta * tsac_share + gamma * sosac_share`
- Added support for TSAC (land area proportional) and SOSAC (SIDS structural adjustment) components.
- Preserved SIDS eligibility in high-income exclusion mode.
- Implemented SOSAC fallback: reallocates to IUSAF if no eligible SIDS are present.

### User Interface
- Added TSAC and SOSAC sliders to the Streamlit sidebar in `app.py`.
- Updated slider defaults and ranges to keep stewardship adjustments secondary to IUSAF:
  - Initial load default: TSAC `0.00`, SOSAC `0.00` (true equality)
  - Balanced preset: TSAC `0.05`, SOSAC `0.03`
  - Range: TSAC `0.00-0.15`, SOSAC `0.00-0.10`
- Implemented dynamic interpretation boxes explaining the allocation impact of beta and gamma.
- Added live stewardship status line and threshold-based warnings (`>0.15` mild, `>0.20` strong).
- Added outcome warnings based on equality-reference diagnostics (share below equality and median vs equality reference).
- Added hard-stop guard for invalid blends where `TSAC + SOSAC >= 1.0`.
- Created a "Negotiation Dashboard" tab with Plotly visualizations:
  - Increases/Decreases metrics and bar charts.
  - Group impact analysis.
  - Country-level waterfall charts.
  - Selected-country stewardship scenario comparison chart with equality reference.
- Updated negotiation preset values to align with the revised stewardship caps and defaults.
- Fixed tab NameErrors by using dynamic indexing.

### Testing
- Added comprehensive tests in `tests/test_tsac_sosac.py` and `tests/test_negotiator_dashboard.py`.
- Verified all 67+ tests pass.

## Notes for Next Session
- **UI/UX Refinement**: Continued feedback on the placement and functionality of the negotiation tools is expected.
- Documentation will be needed with numbers for docs showing the raw inversion. Documentation will be beeded for the band inversion explaining the logic and the weightings. 

