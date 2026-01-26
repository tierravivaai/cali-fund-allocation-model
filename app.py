import streamlit as st
import duckdb
import pandas as pd
from logic.data_loader import load_data, get_base_data
from logic.calculator import calculate_allocations, aggregate_by_region, aggregate_eu, aggregate_special_groups

st.set_page_config(page_title="Cali Fund Allocation Model", layout="wide")

st.title("Cali Fund Allocation Model (UN Scale)")
st.markdown("*This interactive tool is provided purely for illustrative and exploratory purposes. It has no status.*")

# Initialize connection and data
if 'con' not in st.session_state:
    st.session_state.con = duckdb.connect(database=':memory:')
    load_data(st.session_state.con)
    st.session_state.base_df = get_base_data(st.session_state.con)

# Sidebar Controls
st.sidebar.header("Controls")

fund_size_bn = st.sidebar.slider(
    "Annual Cali Fund size (USD billion)",
    min_value=0.1,
    max_value=10.0,
    value=1.0,
    step=0.1,
    format="$%.1fbn"
)

iplc_share = st.sidebar.slider(
    "Share earmarked for Indigenous Peoples & Local Communities (%)",
    min_value=50,
    max_value=80,
    value=50,
    help="This splits each Party’s allocation into an IPLC envelope and a State envelope. Together they equal the total."
)

show_raw = st.sidebar.toggle("Show 'raw inversion' and explanation", value=False)

exclude_hi = st.sidebar.checkbox("Exclude High Income countries from receiving allocations", value=False)
st.sidebar.markdown("*“When enabled, High Income countries receive zero allocation and the remaining allocations are rescaled so the total fund remains unchanged.”*")

if st.sidebar.button("Reset to default"):
    st.rerun()

# Calculations
fund_size_usd = fund_size_bn * 1_000_000_000
results_df = calculate_allocations(st.session_state.base_df, fund_size_usd, iplc_share, show_raw, exclude_hi)

# Main Tabs
tab1, tab2, tab2b, tab2c, tab3, tab4, tab5 = st.tabs([
    "By Party (A–Z)", 
    "By UN Region", 
    "By UN Sub-region",
    "By UN Intermediate Region",
    "EU Block", 
    "Developed vs LDC", 
    "SIDS"
])

with tab1:
    st.subheader("Allocations by Country")
    # Add party status column for display
    def get_status(row):
        if not row["is_cbd_party"]:
            return "Non-Party"
        return "Party"
        
    results_df["Party Status"] = results_df.apply(get_status, axis=1)
    
    display_cols = ['party', 'total_allocation', 'state_envelope', 'iplc_envelope', 'World Bank Income Group', 'Party Status']
    if show_raw:
        st.info("""
    **How the Calculation Works in Plain Language**

This model uses an inverted version of the UN Scale of Assessments, which is a widely used measure of countries’ relative economic capacity.

In simple terms, countries that have a smaller assessed share of the UN budget receive a larger share of this fund, and countries with a larger assessed share receive a smaller share.

Simple examples

**Country A (smaller assessed share)**
Suppose Country A’s UN assessment is 0.001%. Because this is a very small share, the model gives Country A a relatively large weight, which results in a larger share of the Cali Fund.

**Country B (larger assessed share)**
Suppose Country B’s UN assessment is 10%. Because this is a much larger share, the model gives Country B a relatively smaller weight, which results in a smaller share of the Cali Fund.

Final step

After these weights are calculated, the results are scaled so that the total amount distributed exactly equals the fund size you select in the sidebar.
    """)
        
        with st.expander("How the calculation works (technical summary)"):
            st.markdown("For each Party, the calculation proceeds in four steps:")
            
            st.markdown("""
            1. **Inversion**
            Each Party’s UN Scale of Assessments share (expressed as a percentage) is inverted by taking its reciprocal (that is, dividing 1 by the share). This means Parties with smaller assessed shares receive larger weights.
            """)
            
            st.markdown("""
            2. **Normalisation**
            All inverted values are summed, and each Party’s inverted value is divided by this total. This produces a set of shares that sum exactly to 100%.
            """)
            
            st.markdown("""
            3. **Allocation**
            Each Party’s share is multiplied by the total fund size (for example, USD 1 billion) to determine its total annual allocation.
            """)
            
            st.markdown("""
            4. **Earmarking**
            The total allocation is then split into a State Envelope and an Indigenous Peoples and Local Communities (IPLC) Envelope according to the percentage selected.
            """)
        
        display_cols.insert(1, 'un_share')
        display_cols.insert(2, 'un_share_fraction')
        display_cols.insert(3, 'inverted_share')
    
    search = st.text_input("Search Country", "")
    filtered_df = results_df[results_df['party'].str.contains(search, case=False)]
    
    def style_rows(row):
        if not row["eligible"]:
            return ['background-color: #f0f0f0; color: #a0a0a0'] * len(row)
        return [''] * len(row)

    st.dataframe(
        filtered_df[display_cols + ["eligible"]].sort_values('party').style.apply(style_rows, axis=1),
        column_config={
            "eligible": None, # Hide this column
            "party": "Country",
            "total_allocation": st.column_config.NumberColumn("Total (USD Millions)", format="$%.2f"),
            "state_envelope": st.column_config.NumberColumn("State (USD Millions)", format="$%.2f"),
            "iplc_envelope": st.column_config.NumberColumn("IPLC (USD Millions)", format="$%.2f"),
            "un_share": st.column_config.NumberColumn("UN Share (%)", format="%.4f"),
            "un_share_fraction": st.column_config.NumberColumn("UN Share (fraction)", format="%.6f"),
            "inverted_share": st.column_config.NumberColumn("Inv Share (normalised)", format="%.6f"),
        },
        hide_index=True,
        use_container_width=True
    )

with tab2:
    st.subheader("Totals by UN Region")
    region_df = aggregate_by_region(results_df, 'region')
    st.dataframe(
        region_df.sort_values('total_allocation', ascending=False),
        column_config={
            "total_allocation": st.column_config.NumberColumn("Total (USD Millions)", format="$%.2f"),
            "state_envelope": st.column_config.NumberColumn("State (USD Millions)", format="$%.2f"),
            "iplc_envelope": st.column_config.NumberColumn("IPLC (USD Millions)", format="$%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )

with tab2b:
    st.subheader("Totals by UN Sub-region")
    sub_region_df = aggregate_by_region(results_df, 'sub_region')
    st.dataframe(
        sub_region_df.sort_values('total_allocation', ascending=False),
        column_config={
            "total_allocation": st.column_config.NumberColumn("Total (USD Millions)", format="$%.2f"),
            "state_envelope": st.column_config.NumberColumn("State (USD Millions)", format="$%.2f"),
            "iplc_envelope": st.column_config.NumberColumn("IPLC (USD Millions)", format="$%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )

with tab2c:
    st.subheader("Totals by UN Intermediate Region")
    int_region_df = aggregate_by_region(results_df[results_df['intermediate_region'] != 'NA'], 'intermediate_region')
    st.dataframe(
        int_region_df.sort_values('total_allocation', ascending=False),
        column_config={
            "total_allocation": st.column_config.NumberColumn("Total (USD Millions)", format="$%.2f"),
            "state_envelope": st.column_config.NumberColumn("State (USD Millions)", format="$%.2f"),
            "iplc_envelope": st.column_config.NumberColumn("IPLC (USD Millions)", format="$%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )

with tab3:
    st.subheader("European Union Block View")
    eu_df, eu_total = aggregate_eu(results_df)
    
    st.dataframe(
        eu_df[['party', 'total_allocation', 'state_envelope', 'iplc_envelope']].sort_values('party'),
        column_config={
            "party": "Country",
            "total_allocation": st.column_config.NumberColumn("Total (USD Millions)", format="$%.2f"),
            "state_envelope": st.column_config.NumberColumn("State (USD Millions)", format="$%.2f"),
            "iplc_envelope": st.column_config.NumberColumn("IPLC (USD Millions)", format="$%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.metric("EU Block Total Allocation", f"${eu_total['total_allocation']:,.2f}m")
    col1, col2 = st.columns(2)
    col1.metric("EU Block State Envelope", f"${eu_total['state_envelope']:,.2f}m")
    col2.metric("EU Block IPLC Envelope", f"${eu_total['iplc_envelope']:,.2f}m")

with tab4:
    st.subheader("Developed vs Least Developed Countries (LDC)")
    ldc_total, _ = aggregate_special_groups(results_df)
    
    # Calculate non-LDC (broadly 'Developed/Other')
    non_ldc_total = results_df[~results_df['is_ldc']][['total_allocation', 'state_envelope', 'iplc_envelope']].sum()
    
    summary_data = pd.DataFrame([
        {"Group": "Least Developed Countries (LDC)", **ldc_total.to_dict()},
        {"Group": "Other Countries", **non_ldc_total.to_dict()}
    ])
    
    st.dataframe(
        summary_data,
        column_config={
            "total_allocation": st.column_config.NumberColumn("Total (USD Millions)", format="$%.2f"),
            "state_envelope": st.column_config.NumberColumn("State (USD Millions)", format="$%.2f"),
            "iplc_envelope": st.column_config.NumberColumn("IPLC (USD Millions)", format="$%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )

with tab5:
    st.subheader("Small Island Developing States (SIDS)")
    _, sids_total = aggregate_special_groups(results_df)
    
    st.metric("Total SIDS Allocation", f"${sids_total['total_allocation']:,.2f}m")
    col1, col2 = st.columns(2)
    col1.metric("SIDS State Envelope", f"${sids_total['state_envelope']:,.2f}m")
    col2.metric("SIDS IPLC Envelope", f"${sids_total['iplc_envelope']:,.2f}m")

st.divider()
st.markdown("""
**Notes**  
The allocations shown are indicative and are generated using an inverted [UN Scale of Assessments](https://digitallibrary.un.org/record/4071844?ln=en&utm_source=chatgpt.com&v=pdf#files) for the years 2025-2027 to support discussion. Definitions of UN regions, Least developed countries (LDC) and Small Island Developing States (SIDS) are from the [UNSD M49](https://unstats.un.org/unsd/methodology/m49/) standard. [World Bank Income Classification groups](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups) are shown to assist with interpretation and to enable the ability to toggle high income (developed) countries on or off in calculations.
""")
