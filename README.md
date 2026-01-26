# Cali Allocation Model (UN Scale)

This interactive tool illustrates how Cali Fund allocations would be distributed if based on the **latest UN Scale of Assessments (2025-2027)**, inverted to reflect relative need.

## Features
- **Adjustable Fund Size**: Scale the annual Cali Fund from $0.1bn to $10.0bn.
- **IPLC Earmark**: Set the percentage earmarked for Indigenous Peoples & Local Communities (50% to 80%).
- **Multi-perspective views**:
    - Detailed Party-level table.
    - Regional aggregations (UNSD M49).
    - EU Block summary.
    - Developmental groupings (LDC, SIDS).
- **Transparency**: Toggle "Raw Inversion" to see the underlying mathematical shares.

## Installation & Setup

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Methodology
The model takes each Party's UN Scale of Assessment share for 2027 and inverts it. This means countries with a smaller UN share (typically lower-income countries) receive a larger portion of the Cali Fund.

## Data Sources
- **UN Scale of Assessments**: General assembly resolution 79/225.
- **Regions**: UNSD M49 standard.
- **Income Class**: World Bank Country and Lending Groups.
