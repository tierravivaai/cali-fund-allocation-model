import streamlit as st
import duckdb
import pandas as pd
from logic.data_loader import load_data, get_base_data
from logic.calculator import calculate_allocations, aggregate_by_region, aggregate_eu, aggregate_special_groups, aggregate_by_income

st.set_page_config(page_title="Cali Fund Allocation Model", layout="wide")

st.title("Cali Fund Allocation Model (UN Scale)")
st.markdown("""
This interactive tool uses the UN Scale of Assessments (2025–2027) to model indicative shares of the Cali Fund. The model inverts assessed UN budget shares so that countries with smaller assessed shares receive proportionally larger indicative allocations. 

This interactive tool is provided purely for illustrative and exploratory purposes. 
IPLC figures are shown for illustrative purposes only and do not imply any specific delivery or governance arrangement. This tool has no formal status.

A detailed description of the UN Scale of Assessment for 2025-2027 is available [here](https://www.un-ilibrary.org/content/books/9789211069945c004/read) and the latest table is [here](https://digitallibrary.un.org/record/4071844?ln=en&utm_source=chatgpt.com&v=pdf#files).
""")

# Initialize connection and data
if 'con' not in st.session_state:
    st.session_state.con = duckdb.connect(database=':memory:')
    load_data(st.session_state.con)
    st.session_state.base_df = get_base_data(st.session_state.con)

# Sidebar Controls
st.sidebar.header("Controls")

# Reset to default button
if st.sidebar.button("Reset to default"):
    for key in ["fund_size_bn", "iplc_share", "show_raw", "use_thousands", "exclude_hi"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

fund_size_bn = st.sidebar.slider(
    "Annual Cali Fund size (USD billion)",
    min_value=0.002,   # $2m
    max_value=10.0,
    value=1.0,         # keep default as-is ($1bn)
    step=0.001,        # $1m increments
    format="$%.3fbn",
    key="fund_size_bn"
)
st.sidebar.caption(f"= ${fund_size_bn * 1000:,.0f} million per year")

iplc_share = st.sidebar.slider(
    "Share earmarked for Indigenous Peoples & Local Communities (%)",
    min_value=50,
    max_value=80,
    value=50,
    help="This splits each Party’s allocation into an IPLC envelope and a State envelope. Together they equal the total.",
    key="iplc_share"
)

show_raw = st.sidebar.toggle("Show explanation with raw data", value=False, key="show_raw")

use_thousands = st.sidebar.toggle("Display small values in thousands (USD '000)", value=False, key="use_thousands")

exclude_hi = st.sidebar.checkbox("Exclude High Income countries from receiving allocations", value=True, key="exclude_hi")
st.sidebar.markdown("*“When enabled, High Income countries receive zero allocation and the remaining allocations are rescaled so the total fund remains unchanged.”*")

sort_option = st.sidebar.selectbox(
    "Sort results by",
    options=["Allocation (highest first)", "Country name (A–Z)"],
    index=0,
    key="sort_option"
)

# Calculations
fund_size_usd = fund_size_bn * 1_000_000_000
results_df = calculate_allocations(st.session_state.base_df, fund_size_usd, iplc_share, show_raw, exclude_hi)

# Apply sorting
if sort_option == "Allocation (highest first)":
    results_df = results_df.sort_values(
        by=["total_allocation", "party"],
        ascending=[False, True]
    ).reset_index(drop=True)
    results_df.index = results_df.index + 1
    results_df.index.name = "Rank"
else:
    results_df = results_df.sort_values(
        by="party",
        ascending=True
    ).reset_index(drop=True)

def format_currency(val):
    if use_thousands and val < 1.0:
        return f"${val * 1000:,.2f}k"
    return f"${val:,.2f}m"

# Helper for dataframe formatting
def get_column_config(use_thousands):
    if use_thousands:
        # When using thousands, we must use TextColumn because we mix 'k' and 'm'
        return {
            "total_allocation": st.column_config.TextColumn("Total Share (USD)"),
            "state_envelope": st.column_config.TextColumn("State Envelope (USD)"),
            "iplc_envelope": st.column_config.TextColumn("IPLC Envelope (USD)"),
        }
    else:
        # Standard millions view can use NumberColumn for better sorting
        return {
            "total_allocation": st.column_config.NumberColumn("Total Share (USD Millions)", format="$%.2f"),
            "state_envelope": st.column_config.NumberColumn("State Envelope (USD Millions)", format="$%.2f"),
            "iplc_envelope": st.column_config.NumberColumn("IPLC Envelope (USD Millions)", format="$%.2f"),
        }

# Main Tabs
tab1, tab2, tab2b, tab2c, tab3, tab3b, tab4, tab5 = st.tabs([
    "By Party", 
    "By UN Region", 
    "By UN Sub-region",
    "By UN Intermediate Region",
    "EU Block", 
    "Share by Income Group",
    "LDC Share", 
    "SIDS"
])

with tab1:
    st.subheader("Allocations by Country")
    # Add party status column for display
    def get_status(row):
        if not row["is_cbd_party"]:
            return "Non-Party"
        return "Party"
        
    results_df["CBD Party Status"] = results_df.apply(get_status, axis=1)
    results_df["World Bank income group"] = results_df["World Bank Income Group"]
    
    display_cols = ['party', 'total_allocation', 'state_envelope', 'iplc_envelope', 'World Bank income group', 'CBD Party Status']
    if show_raw:
        st.info("""
    **How the Calculation Works (Plain Language)**

This model uses an inverted version of the UN Scale of Assessments, which is a widely used measure of countries’ relative economic capacity.

In simple terms, countries with a smaller assessed share of the UN budget receive a larger indicative share of this fund, while countries with a larger assessed share receive a smaller indicative share.

Simple examples

Country A (smaller assessed share)
Suppose Country A’s UN assessment is 0.001%. Because this is a very small assessed share, the model assigns Country A a relatively large weight, which results in a larger share of the Cali Fund.

Country B (larger assessed share)
Suppose Country B’s UN assessment is 10%. Because this is a much larger assessed share, the model assigns Country B a relatively smaller weight, which results in a smaller share of the Cali Fund.

(Behind the scenes, assessed shares are first converted from percentages into standard numerical values before being inverted. This is a technical step required for the calculation and does not affect the overall logic.)

Final step

After these weights are calculated, they are rescaled so that the total amount distributed exactly equals the fund size selected in the sidebar. Each Party’s total allocation is then divided into a State Envelope and an Indigenous Peoples and Local Communities (IPLC) Envelope according to the selected percentage.
    """)
        
        with st.expander("How the calculation works (technical summary)"):
            st.markdown("For each Party, the calculation proceeds in four steps:")
            
            st.markdown("""
            1. **Inversion**
            Each Party’s UN Scale of Assessments share is first converted from a percentage into a decimal (for example, 0.005% becomes 0.00005).

            The model then inverts this value by taking its reciprocal (that is, dividing 1 by the decimal value). This produces an inverse weight.

            2. **Normalisation**
            All inverse weights are summed, and each Party’s weight is divided by this total. This produces a set of shares that sum exactly to 100%.

            3. **Allocation**
            Each Party’s share is multiplied by the total fund size to determine its indicative allocation.

            4. **Earmarking**
            The allocation is then divided into a State envelope and an IPLC envelope according to the selected percentage.
            """)
        
        display_cols.insert(1, 'un_share')
        display_cols.insert(2, 'inverted_share')
    
    search = st.text_input("Search Country", "")
    filtered_df = results_df[results_df['party'].str.contains(search, case=False)].copy()
    
    # Only apply string formatting if toggle is ON; otherwise use numeric for sorting
    if use_thousands:
        for col in ['total_allocation', 'state_envelope', 'iplc_envelope']:
            filtered_df[col] = filtered_df[col].apply(format_currency)
    
    config = {
        "eligible": None, # Hide this column
        "party": "Country",
        "un_share": st.column_config.NumberColumn("UN assessed share (%)", format="%.4f"),
        "un_share_fraction": st.column_config.NumberColumn("UN assessed share (fraction)", format="%.6f"),
        "inverted_share": st.column_config.NumberColumn("Indicative share of Cali Fund (%)", format="%.6f"),
    }
    config.update(get_column_config(use_thousands))

    # Determine whether to hide index based on sorting
    hide_index = (sort_option == "Country name (A–Z)")

    st.dataframe(
        filtered_df[display_cols + ["eligible"]],
        column_config=config,
        hide_index=hide_index,
        use_container_width=True
    )


with tab2:
    st.subheader("Totals by UN Region")
    region_df = aggregate_by_region(results_df, 'region')
    if use_thousands:
        for col in ['total_allocation', 'state_envelope', 'iplc_envelope']:
            region_df[col] = region_df[col].apply(format_currency)
    st.dataframe(
        region_df.sort_values('total_allocation', ascending=False),
        column_config=get_column_config(use_thousands),
        hide_index=True,
        use_container_width=True
    )

with tab2b:
    st.subheader("Totals by UN Sub-region")
    sub_region_df = aggregate_by_region(results_df, 'sub_region')
    if use_thousands:
        for col in ['total_allocation', 'state_envelope', 'iplc_envelope']:
            sub_region_df[col] = sub_region_df[col].apply(format_currency)
    st.dataframe(
        sub_region_df.sort_values('total_allocation', ascending=False),
        column_config=get_column_config(use_thousands),
        hide_index=True,
        use_container_width=True
    )

with tab2c:
    st.subheader("Totals by UN Intermediate Region")
    int_region_df = aggregate_by_region(results_df[results_df['intermediate_region'] != 'NA'], 'intermediate_region')
    if use_thousands:
        for col in ['total_allocation', 'state_envelope', 'iplc_envelope']:
            int_region_df[col] = int_region_df[col].apply(format_currency)
    st.dataframe(
        int_region_df.sort_values('total_allocation', ascending=False),
        column_config=get_column_config(use_thousands),
        hide_index=True,
        use_container_width=True
    )

with tab3:
    st.subheader("European Union Block View")
    eu_df, eu_total = aggregate_eu(results_df)
    
    display_eu_df = eu_df.copy()
    if use_thousands:
        for col in ['total_allocation', 'state_envelope', 'iplc_envelope']:
            display_eu_df[col] = display_eu_df[col].apply(format_currency)

    config = {"party": "Country"}
    config.update(get_column_config(use_thousands))

    st.dataframe(
        display_eu_df[['party', 'total_allocation', 'state_envelope', 'iplc_envelope']].sort_values('party'),
        column_config=config,
        hide_index=True,
        use_container_width=True
    )
    
    st.metric("EU Block Total Allocation", format_currency(eu_total['total_allocation']))
    col1, col2 = st.columns(2)
    col1.metric("EU Block State Envelope", format_currency(eu_total['state_envelope']))
    col2.metric("EU Block IPLC Envelope", format_currency(eu_total['iplc_envelope']))

with tab3b:
    st.subheader("Totals by World Bank Income Group")
    income_df = aggregate_by_income(results_df)
    if use_thousands:
        for col in ['total_allocation', 'state_envelope', 'iplc_envelope']:
            income_df[col] = income_df[col].apply(format_currency)
    
    config = {"World Bank Income Group": "Income Group"}
    config.update(get_column_config(use_thousands))
    
    st.dataframe(
        income_df.sort_values('total_allocation', ascending=False),
        column_config=config,
        hide_index=True,
        use_container_width=True
    )

with tab4:
    st.subheader("LDC Share")
    ldc_total, _ = aggregate_special_groups(results_df)
    
    # Calculate non-LDC (broadly 'Developed/Other')
    non_ldc_total = results_df[~results_df['is_ldc']][['total_allocation', 'state_envelope', 'iplc_envelope']].sum()
    
    summary_data = pd.DataFrame([
        {"Group": "Least Developed Countries (LDC)", **ldc_total.to_dict()},
        {"Group": "Other Countries", **non_ldc_total.to_dict()}
    ])
    if use_thousands:
        for col in ['total_allocation', 'state_envelope', 'iplc_envelope']:
            summary_data[col] = summary_data[col].apply(format_currency)
    
    st.dataframe(
        summary_data,
        column_config=get_column_config(use_thousands),
        hide_index=True,
        use_container_width=True
    )

with tab5:
    st.subheader("Small Island Developing States (SIDS)")
    _, sids_total = aggregate_special_groups(results_df)
    
    st.metric("Total SIDS Allocation", format_currency(sids_total['total_allocation']))
    col1, col2 = st.columns(2)
    col1.metric("SIDS State Envelope", format_currency(sids_total['state_envelope']))
    col2.metric("SIDS IPLC Envelope", format_currency(sids_total['iplc_envelope']))

st.divider()
st.markdown("""
**Notes**  
The allocations shown are indicative and are generated using an inverted [UN Scale of Assessments](https://digitallibrary.un.org/record/4071844?ln=en&utm_source=chatgpt.com&v=pdf#files) for the years 2025-2027 to support discussion. Definitions of UN regions, Least developed countries (LDC) and Small Island Developing States (SIDS) are from the [UNSD M49](https://unstats.un.org/unsd/methodology/m49/) standard. [World Bank Income Classification groups](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups) are shown to assist with interpretation and to enable the ability to toggle high income (developed) countries on or off in calculations.

---
Prepared by Paul Oldham [TierraViva AI](https://www.tierraviva.ai/). Developed with Droid by [Factory AI](https://factory.ai/). Source code available on [Github](https://github.com/tierravivaai/cali-fund-allocation-model)
""")
