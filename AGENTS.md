# Agent Instructions: Cali Allocation Model

## Context
You are working on a policy-support tool for biodiversity fund allocation (Cali Fund). The model uses the inverted UN Scale of Assessments to determine distribution among Parties.

## Core Rules
1. **Inversion & Blending Logic**: 
   - **IUSAF Weight** = `1 / un_share_2027` (Normalised to sum to 1.0).
   - **TSAC Weight** = Proportional to `land_area_km2` (Normalised to sum to 1.0).
   - **SOSAC Weight** = Equal share for all eligible SIDS (Normalised to sum to 1.0).
   - `Final Share = (1 - beta - gamma) * iusaf_share + beta * tsac_share + gamma * sosac_share`.
   - `allocation = fund_size * Final Share`.
2. **Data Consistency**:
   - Total allocations MUST sum to the specified fund size.
   - `Total = IPLC Envelope + State Envelope`.
3. **Labels Only**:
   - WB income groups and UNSD regions are for descriptive purposes only. They must NOT influence the calculation logic.
4. **EU Handling**:
   - The "European Union" is a Party but usually has 0% on the UN scale. 
   - Display it with 0 USD allocation in individual tables.
   - Include it in the "EU Block" aggregate view along with individual Member States.
5. **Exclusions**:
   - Land Locked Developing Countries (LLDC) are NOT currently explicitly excluded, but the UI focuses on LDC and SIDS.
   - High Income countries can be toggled on/off (off by default on initial load to support true-equality start).

6. **New Features**:
   - "Plain Language" and "Technical Summary" sections for explaining the model.
   - "Share by Income Group" tab.
   - "Negotiation Dashboard" with Plotly-based visualizations for baseline comparison and sensitivity analysis.
   - Consistent "State then IPLC" column ordering.

## Technical Stack
- **Backend**: DuckDB for SQL-based data transformations.
- **Frontend**: Streamlit for the interactive dashboard.
- **Testing**: Pytest for mathematical verification.
