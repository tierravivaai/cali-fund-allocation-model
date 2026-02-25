import streamlit as st
import duckdb
import pandas as pd
from logic.data_loader import load_data, get_base_data
from logic.calculator import calculate_allocations, aggregate_by_region, aggregate_eu, aggregate_special_groups, aggregate_by_income

st.set_page_config(page_title="Cali Fund Allocation Model", layout="wide")

st.title("Cali Fund Allocation Model (UN Scale)")
st.markdown("""
This interactive application uses the UN Scale of Assessments (2025–2027) to model indicative shares of the Cali Fund. The model inverts assessed UN budget shares so that countries with smaller assessed shares receive proportionally larger indicative allocations. 

All figures are illustrative modelling outputs for exploratory purposes. They do not represent entitlements or predetermined disbursements.
The IPLC component reflects the share of resources expected to support indigenous peoples and local communities consistent with existing COP decisions. 
Governance arrangements are determined separately. The model has no formal status.

A detailed description of the UN Scale of Assessment for 2025-2027 is available [here](https://www.un-ilibrary.org/content/books/9789211069945c004/read) and the latest table is [here](https://digitallibrary.un.org/record/4071844?ln=en&utm_source=chatgpt.com&v=pdf#files).
""")

# Initialize connection and data
if 'con' not in st.session_state:
    st.session_state.con = duckdb.connect(database=':memory:')
    load_data(st.session_state.con)
    st.session_state.base_df = get_base_data(st.session_state.con)

# Initialize widget states
if "fund_size_bn" not in st.session_state:
    st.session_state["fund_size_bn"] = 1.0
if "iplc_share" not in st.session_state:
    st.session_state["iplc_share"] = 50
if "show_raw" not in st.session_state:
    st.session_state["show_raw"] = False
if "use_thousands" not in st.session_state:
    st.session_state["use_thousands"] = False
if "exclude_hi" not in st.session_state:
    st.session_state["exclude_hi"] = True
if "enable_floor" not in st.session_state:
    st.session_state["enable_floor"] = False
if "floor_pct" not in st.session_state:
    st.session_state["floor_pct"] = 0.05
if "enable_ceiling" not in st.session_state:
    st.session_state["enable_ceiling"] = False
if "ceiling_pct" not in st.session_state:
    st.session_state["ceiling_pct"] = 2.0
if "sort_option" not in st.session_state:
    st.session_state["sort_option"] = "Allocation (highest first)"

# Sidebar Controls
st.sidebar.header("Controls")

# Reset to default button
if st.sidebar.button("Reset to default"):
    st.session_state["fund_size_bn"] = 1.0
    st.session_state["iplc_share"] = 50
    st.session_state["show_raw"] = False
    st.session_state["use_thousands"] = False
    st.session_state["exclude_hi"] = True
    st.session_state["enable_floor"] = False
    st.session_state["floor_pct"] = 0.05
    st.session_state["enable_ceiling"] = False
    st.session_state["ceiling_pct"] = 2.0
    st.session_state["sort_option"] = "Allocation (highest first)"
    st.rerun()

fund_size_bn = st.sidebar.slider(
    "Annual Cali Fund size (USD billion)",
    min_value=0.002,   # $2m
    max_value=10.0,
    step=0.001,        # $1m increments
    format="$%.3fbn",
    key="fund_size_bn"
)
st.sidebar.caption(f"= ${fund_size_bn * 1000:,.0f} million per year")

iplc_share = st.sidebar.slider(
    "Share earmarked for Indigenous Peoples & Local Communities (%)",
    min_value=50,
    max_value=80,
    help="This splits each Party’s allocation into an IPLC component and a State component. Together they equal the total.",
    key="iplc_share"
)

# Calculations Pre-setup
fund_size_usd = fund_size_bn * 1_000_000_000

exclude_hi = st.sidebar.checkbox("Exclude High Income countries from receiving allocations", key="exclude_hi")
st.sidebar.markdown("*“When enabled, High Income countries receive zero allocation and the remaining allocations are rescaled so the total fund remains unchanged.”*")

enable_floor = st.sidebar.checkbox("Enable minimum share (floor)", key="enable_floor")
if enable_floor:
    eligible_mask = st.session_state.base_df["is_cbd_party"].astype(bool)
    if exclude_hi:
        eligible_mask = eligible_mask & (st.session_state.base_df["WB Income Group"] != "High income")

    n_eligible = int(eligible_mask.sum())
    max_floor_pct = 0.0 if n_eligible <= 0 else (100.0 / n_eligible)

    floor_pct = st.sidebar.slider(
        "Minimum share per eligible country (% of total fund)",
        min_value=0.00,
        max_value=float(max_floor_pct),
        value=min(0.05, float(max_floor_pct)),
        step=0.01,
        format="%.2f",
        help=(
            "Sets a minimum percentage of the total fund for each eligible country. "
            "The maximum possible value is automatically limited to 100% divided by the number of eligible countries "
            "to ensure the model remains feasible."
        ),
        key="floor_pct"
    )

    st.sidebar.caption(
        f"Eligible countries: {n_eligible} • "
        f"Max feasible floor: {max_floor_pct:.2f}% • "
        f"Floor ≈ ${fund_size_usd * (floor_pct/100) / 1_000_000:,.2f}m per eligible country"
    )
else:
    floor_pct = 0.0

enable_ceiling = st.sidebar.checkbox("Enable maximum share (ceiling)", key="enable_ceiling")
if enable_ceiling:
    ceiling_pct = st.sidebar.slider(
        "Maximum share per eligible country (% of total fund)",
        min_value=0.50,
        max_value=5.00,
        step=0.10,
        format="%.2f",
        key="ceiling_pct"
    )
    st.sidebar.caption(
        f"≈ ${fund_size_usd * (ceiling_pct/100) / 1_000_000:,.2f}m per eligible country"
    )

    with st.sidebar.expander("More ceiling options"):
        ceiling_pct_ext = st.slider(
            "Maximum share per eligible country (% of total fund) — extended range",
            min_value=5.00,
            max_value=20.00,
            value=st.session_state.get("ceiling_pct_ext", max(5.0, ceiling_pct)),
            step=0.50,
            format="%.2f",
            key="ceiling_pct_ext"
        )
        # Use the extended one if the primary one is at its max
        if ceiling_pct >= 5.0:
            ceiling_pct = ceiling_pct_ext
            
        st.caption(
            f"≈ ${fund_size_usd * (ceiling_pct/100) / 1_000_000:,.2f}m per eligible country"
        )
else:
    ceiling_pct = None


show_raw = st.sidebar.toggle("Show explanation with raw data", key="show_raw")

use_thousands = st.sidebar.toggle("Display small values in thousands (USD '000)", key="use_thousands")

sort_option = st.sidebar.selectbox(
    "Sort results by",
    options=["Allocation (highest first)", "Country name (A–Z)"],
    key="sort_option"
)

results_df = calculate_allocations(
    st.session_state.base_df,
    fund_size_usd,
    iplc_share,
    show_raw,
    exclude_hi,
    floor_pct=floor_pct,
    ceiling_pct=ceiling_pct
)

# Add descriptive columns
results_df["EU"] = results_df["is_eu_ms"].map({True: "EU Member", False: "Non-EU"})
results_df["UN LDC"] = results_df["is_ldc"].map({True: "LDC", False: "-"})

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
            "state_component": st.column_config.TextColumn("State Component (USD)"),
            "iplc_component": st.column_config.TextColumn("IPLC Component (USD)"),
        }
    else:
        # Standard millions view can use NumberColumn for better sorting
        return {
            "total_allocation": st.column_config.NumberColumn("Total Share (USD Millions)", format="$%.2f"),
            "state_component": st.column_config.NumberColumn("State Component (USD Millions)", format="$%.2f"),
            "iplc_component": st.column_config.NumberColumn("IPLC Component (USD Millions)", format="$%.2f"),
        }

# Main Tabs
tab1, tab2, tab2b, tab2c, tab3b, tab4, tab5b, tab6, tab7, tab5 = st.tabs([
    "By Party", 
    "By UN Region", 
    "By UN Sub-region",
    "By UN Intermediate Region",
    "Share by Income Group",
    "LDC Share", 
    "Low Income",
    "Middle Income",
    "High Income",
    "SIDS"
])

with tab1:
    st.subheader("Allocations by Country")
    # Add party status column for display
    def get_status(row):
        if not row["is_cbd_party"]:
            return "Non-Party"
        return "Party"
        
    results_df["CBD Party"] = results_df.apply(get_status, axis=1)
    
    display_cols = ['party', 'total_allocation', 'state_component', 'iplc_component', 'WB Income Group', 'UN LDC', 'CBD Party', 'EU']
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

After these weights are calculated, they are rescaled so that the total amount distributed exactly equals the fund size selected in the sidebar. Each Party’s total allocation is then divided into a State Component and an Indigenous Peoples and Local Communities (IPLC) Component according to the selected percentage.

For more detailed information see this [walkthrough](https://github.com/tierravivaai/cali-fund-allocation-model/blob/main/walkthrough.md)
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
            The allocation is then divided into a State component and an IPLC component according to the selected percentage.

            For more detailed information see this [walkthrough](https://github.com/tierravivaai/cali-fund-allocation-model/blob/main/walkthrough.md)
            """)
        
        display_cols.insert(1, 'un_share')
        display_cols.insert(2, 'inverted_share')
    
    search = st.text_input("Search Country", "")
    filtered_df = results_df[results_df['party'].str.contains(search, case=False)].copy()
    
    # Only apply string formatting if toggle is ON; otherwise use numeric for sorting
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
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
        for col in ['total_allocation', 'state_component', 'iplc_component']:
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
        for col in ['total_allocation', 'state_component', 'iplc_component']:
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
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            int_region_df[col] = int_region_df[col].apply(format_currency)
    st.dataframe(
        int_region_df.sort_values('total_allocation', ascending=False),
        column_config=get_column_config(use_thousands),
        hide_index=True,
        use_container_width=True
    )

with tab3b:
    st.subheader("Totals by World Bank Income Group")
    income_df = aggregate_by_income(results_df)
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            income_df[col] = income_df[col].apply(format_currency)
    
    config = {"WB Income Group": "Income Group"}
    config.update(get_column_config(use_thousands))
    
    st.dataframe(
        income_df.sort_values('total_allocation', ascending=False),
        column_config=config,
        hide_index=True,
        use_container_width=True
    )

with tab4:
    st.subheader("LDC Share")
    st.markdown("Least Developed Countries (LDCs) are low-income countries as defined by the UN Committee for Development Policy (CDP) as described [here](https://policy.desa.un.org/least-developed-countries). There are currently 44 LDCs.")
    ldc_total, _ = aggregate_special_groups(results_df)
    
    # Calculate non-LDC (broadly 'Developed/Other')
    non_ldc_total = results_df[~results_df['is_ldc']][['total_allocation', 'state_component', 'iplc_component']].sum()
    
    summary_data = pd.DataFrame([
        {"Group": "Least Developed Countries (LDC)", **ldc_total.to_dict()},
        {"Group": "Other Countries", **non_ldc_total.to_dict()}
    ])
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            summary_data[col] = summary_data[col].apply(format_currency)
    
    st.dataframe(
        summary_data,
        column_config=get_column_config(use_thousands),
        hide_index=True,
        use_container_width=True
    )

with tab5b:
    st.subheader("Low Income Countries")
    li_df = results_df[results_df['WB Income Group'] == 'Low income'].copy()
    
    display_li_df = li_df.copy()
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            display_li_df[col] = display_li_df[col].apply(format_currency)

    config = {
        "party": "Country",
        "WB Income Group": "WB Classification"
    }
    config.update(get_column_config(use_thousands))

    st.dataframe(
        display_li_df[['party', 'total_allocation', 'state_component', 'iplc_component', 'WB Income Group', 'UN LDC']].sort_values('party'),
        column_config=config,
        hide_index=True,
        use_container_width=True
    )
    
    li_total = li_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    st.metric("Low Income Total Allocation", format_currency(li_total['total_allocation']))
    col1, col2 = st.columns(2)
    col1.metric("Low Income State Component", format_currency(li_total['state_component']))
    col2.metric("Low Income IPLC Component", format_currency(li_total['iplc_component']))

with tab6:
    st.subheader("Middle Income Countries")
    mi_df = results_df[results_df['WB Income Group'].isin(['Lower middle income', 'Upper middle income'])].copy()
    
    display_mi_df = mi_df.copy()
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            display_mi_df[col] = display_mi_df[col].apply(format_currency)

    config = {
        "party": "Country",
        "WB Income Group": "WB Classification"
    }
    config.update(get_column_config(use_thousands))

    st.dataframe(
        display_mi_df[['party', 'total_allocation', 'state_component', 'iplc_component', 'UN LDC', 'WB Income Group']].sort_values('party'),
        column_config=config,
        hide_index=True,
        use_container_width=True
    )
    
    mi_total = mi_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    st.metric("Middle Income Countries Total Allocation", format_currency(mi_total['total_allocation']))
    col1, col2 = st.columns(2)
    col1.metric("Middle Income State Component", format_currency(mi_total['state_component']))
    col2.metric("Middle Income IPLC Component", format_currency(mi_total['iplc_component']))

with tab7:
    st.subheader("High Income Countries")
    hi_df = results_df[results_df['WB Income Group'] == 'High income'].copy()
    
    display_hi_df = hi_df.copy()
    if use_thousands:
        for col in ['total_allocation', 'state_component', 'iplc_component']:
            display_hi_df[col] = display_hi_df[col].apply(format_currency)

    config = {"party": "Country"}
    config.update(get_column_config(use_thousands))

    st.dataframe(
        display_hi_df[['party', 'total_allocation', 'state_component', 'iplc_component', 'EU']].sort_values('party'),
        column_config=config,
        hide_index=True,
        use_container_width=True
    )
    
    hi_total = hi_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    st.metric("High Income Total Allocation", format_currency(hi_total['total_allocation']))
    col1, col2 = st.columns(2)
    col1.metric("High Income State Component", format_currency(hi_total['state_component']))
    col2.metric("High Income IPLC Component", format_currency(hi_total['iplc_component']))

with tab5:
    st.subheader("Small Island Developing States (SIDS)")
    _, sids_total = aggregate_special_groups(results_df)
    
    st.metric("Total SIDS Allocation", format_currency(sids_total['total_allocation']))
    col1, col2 = st.columns(2)
    col1.metric("SIDS State Component", format_currency(sids_total['state_component']))
    col2.metric("SIDS IPLC Component", format_currency(sids_total['iplc_component']))

st.divider()
st.markdown("""
**Notes**  
The allocations shown are indicative and are generated using an inverted [UN Scale of Assessments](https://digitallibrary.un.org/record/4071844?ln=en&utm_source=chatgpt.com&v=pdf#files) for the years 2025-2027 to support discussion. Definitions of UN regions, Least developed countries (LDC) and Small Island Developing States (SIDS) are from the [UNSD M49](https://unstats.un.org/unsd/methodology/m49/) standard. [World Bank Income Classification groups](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups) are shown to assist with interpretation and to enable the ability to toggle high income (developed) countries on or off in calculations.

---
Prepared by Paul Oldham [TierraViva AI](https://www.tierraviva.ai/). Developed with Droid by [Factory AI](https://factory.ai/). Source code available on [Github](https://github.com/tierravivaai/cali-fund-allocation-model)
""")
