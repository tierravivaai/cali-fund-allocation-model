import streamlit as st
import pandas as pd
import duckdb
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

from jinja2 import Template

# Page configuration
st.set_page_config(
    page_title="Cali Fund Educational Journey",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
DB_PATH = Path("cali_fund.duckdb")
SQL_MODEL_PATH = Path("model/allocation.sql")

def load_data(params):
    """Run the DuckDB model with given parameters and return the results."""
    con = duckdb.connect(str(DB_PATH))
    
    # Read the SQL model
    sql_template = SQL_MODEL_PATH.read_text()
    
    # Use Jinja2 for robust template rendering
    template = Template(sql_template)
    rendered_sql = template.render(**params)
    
    # Execute the rendered SQL
    con.execute(rendered_sql)
    
    # Fetch results
    df = con.execute("SELECT * FROM allocation_country").df()
    con.close()
    return df

# Sidebar Navigation
st.sidebar.title("Journey Progress")
phases = [
    "Phase 1: Raw Inversion Explorer",
    "Phase 2: Moderation Introduction",
    "Phase 3: Lower Bound Protection",
    "Phase 4: Cap Mechanism",
    "Phase 5: Baseline Blend",
    "Phase 6: Consolidated Working Model"
]

if 'current_phase' not in st.session_state:
    st.session_state.current_phase = 0

selected_phase_idx = st.sidebar.selectbox(
    "Jump to Phase",
    range(len(phases)),
    format_func=lambda x: phases[x],
    index=st.session_state.current_phase
)

st.session_state.current_phase = selected_phase_idx

# Sidebar Controls (Progressive)
st.sidebar.divider()
st.sidebar.subheader("Parameters")

# Fund Size is always available
fund_usd = st.sidebar.slider("Total Fund Size ($B)", 0.1, 5.0, 1.0, 0.1) * 1e9

# Initialize default parameters
params = {
    "fund_usd": fund_usd,
    "iplc_share": 0.5,
    "smoothing_exponent": 1.0, # 1.0 means no smoothing (pure inverse)
    "pct_lower_bound": 0.0,    # 0.0 means no lower bound
    "cap_share": 1.0,          # 1.0 means no cap
    "blend_baseline_share": 0.0, # 0.0 means no baseline blend
    "baseline_recipient": "least developed countries (LDC)"
}

# Add controls based on phase
if st.session_state.current_phase >= 1:
    params["smoothing_exponent"] = st.sidebar.slider("Smoothing Exponent", 0.1, 2.0, 0.5, 0.1)

if st.session_state.current_phase >= 2:
    params["pct_lower_bound"] = st.sidebar.slider("Lower Bound %", 0.0, 0.5, 0.01, 0.005)

if st.session_state.current_phase >= 3:
    params["cap_share"] = st.sidebar.slider("Maximum Cap %", 0.5, 10.0, 2.0, 0.5) / 100.0

if st.session_state.current_phase >= 4:
    params["blend_baseline_share"] = st.sidebar.slider("Baseline Blend Share %", 0, 50, 20, 5) / 100.0
    params["baseline_recipient"] = st.sidebar.selectbox("Baseline Recipient", ["least developed countries (LDC)", "All Parties"])

if st.session_state.current_phase >= 5:
    params["iplc_share"] = st.sidebar.slider("IPLC Share %", 50, 100, 50, 5) / 100.0

# Phase Content
st.title(phases[st.session_state.current_phase])

if st.session_state.current_phase == 0:
    st.markdown("""
    ### The "Ah-ha!" Moment
    **Goal:** Show what pure inverse allocation looks like and why it's impractical.
    
    In this phase, we use the **Raw Inversion** of the CBD Budget percentages. 
    Parties with the *lowest* contributions receive the *highest* shares.
    """)
    
    # Phase 1: Pure Raw Inversion (Smoothing = 1.0, No other protections)
    p1_params = params.copy()
    p1_params["smoothing_exponent"] = 1.0
    p1_params["pct_lower_bound"] = 0.0
    p1_params["cap_share"] = 1.0
    p1_params["blend_baseline_share"] = 0.0
    
    df = load_data(p1_params)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Distribution of Raw Allocations")
        # Color code: Top 10 Green, Bottom 10 Red, Others Gray
        df_sorted = df.sort_values("alloc_usd_m", ascending=False).reset_index(drop=True)
        df_sorted['color'] = 'Middle Range'
        df_sorted.loc[df_sorted.head(10).index, 'color'] = 'Top 10 Allocations'
        df_sorted.loc[df_sorted.tail(10).index, 'color'] = 'Bottom 10 Allocations'
        
        fig = px.bar(
            df_sorted,
            x="party",
            y="alloc_usd_m",
            color="color",
            color_discrete_map={
                'Top 10 Allocations': '#2ecc71',
                'Bottom 10 Allocations': '#e74c3c',
                'Middle Range': '#95a5a6'
            },
            labels={"alloc_usd_m": "Allocation (USD M)", "party": "Party"},
            title="Raw Inversion Results (USD Millions)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Extreme Outcomes")
        top_party = df_sorted.iloc[0]
        bot_party = df_sorted.iloc[-1]
        
        st.metric("Highest Allocation", f"{top_party['party']}", f"${top_party['alloc_usd_m']:.1f}M")
        st.metric("Lowest Allocation", f"{bot_party['party']}", f"${bot_party['alloc_usd_m']:.1f}M")
        
        ratio = top_party['alloc_usd_m'] / bot_party['alloc_usd_m'] if bot_party['alloc_usd_m'] > 0 else 0
        st.metric("Highest/Lowest Ratio", f"{ratio:.1f}x")
        
        st.info(f"**Educational Note:** Notice how Parties with the lowest CBD Budget percentages (like {top_party['party']} at {top_party['cbd_scale_pct']}%) get the highest allocations under raw inversion. This illustrates why moderation is needed.")

    st.subheader("Raw Inversion Results Table")
    st.dataframe(
        df_sorted[['party', 'cbd_scale_pct', 'share_final', 'alloc_usd_m']]
        .rename(columns={
            'party': 'Party',
            'cbd_scale_pct': 'CBD Budget %',
            'share_final': 'Raw Share',
            'alloc_usd_m': 'Allocation (USDM)'
        }),
        use_container_width=True
    )

elif st.session_state.current_phase == 1:
    st.markdown("""
    ### The "Why We Need Safety First" Moment
    **Goal:** Introduce the first moderation mechanism: **Smoothing**.
    
    Smoothing uses an exponent-based dampening to compress the range between highest and lowest allocations.
    """)
    
    # Compare Raw (Phase 1) with Smoothed (Phase 2)
    p1_params = params.copy()
    p1_params["smoothing_exponent"] = 1.0
    p1_params["pct_lower_bound"] = 0.0
    p1_params["cap_share"] = 1.0
    p1_params["blend_baseline_share"] = 0.0
    
    df_raw = load_data(p1_params)
    df_smoothed = load_data(params)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Inversion (Exponent = 1.0)")
        fig_raw = px.bar(df_raw.sort_values("alloc_usd_m", ascending=False), x="party", y="alloc_usd_m")
        st.plotly_chart(fig_raw, use_container_width=True)
        
    with col2:
        st.subheader(f"Smoothed (Exponent = {params['smoothing_exponent']})")
        fig_smooth = px.bar(df_smoothed.sort_values("alloc_usd_m", ascending=False), x="party", y="alloc_usd_m")
        st.plotly_chart(fig_smooth, use_container_width=True)
        
    st.info("**Educational Note:** Smoothing reduces extreme outcomes by compressing the range between highest and lowest allocations. A lower exponent results in a flatter distribution.")

elif st.session_state.current_phase == 2:
    st.markdown("""
    ### The "Protecting the Vulnerable Parties" Moment
    **Goal:** Show how the **Lower Bound** prevents micro-contributors from dominating.
    
    The lower bound sets a minimum CBD contribution percentage for the calculation, which prevents countries with near-zero contributions from receiving disproportionately large shares.
    """)
    
    # Compare Smoothed (Phase 2) with Lower Bound (Phase 3)
    p2_params = params.copy()
    p2_params["pct_lower_bound"] = 0.0
    p2_params["cap_share"] = 1.0
    p2_params["blend_baseline_share"] = 0.0
    
    df_prev = load_data(p2_params)
    df_current = load_data(params)
    
    col1, col2 = st.columns(2)
    
    # Find affected parties
    df_compare = df_prev[['party', 'alloc_usd_m']].merge(df_current[['party', 'alloc_usd_m']], on='party', suffixes=('_old', '_new'))
    df_compare['diff'] = df_compare['alloc_usd_m_new'] - df_compare['alloc_usd_m_old']
    affected = df_compare[abs(df_compare['diff']) > 0.01].sort_values('diff', ascending=False)
    
    with col1:
        st.subheader("Without Lower Bound")
        fig1 = px.bar(df_prev.sort_values("alloc_usd_m", ascending=False).head(20), x="party", y="alloc_usd_m")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader(f"With Lower Bound ({params['pct_lower_bound']}%)")
        fig2 = px.bar(df_current.sort_values("alloc_usd_m", ascending=False).head(20), x="party", y="alloc_usd_m")
        st.plotly_chart(fig2, use_container_width=True)
        
    st.subheader("Top Affected Parties")
    st.table(affected.head(10).rename(columns={'alloc_usd_m_old': 'Old Allocation', 'alloc_usd_m_new': 'New Allocation', 'diff': 'Change'}))
    
    st.info("**Educational Note:** Lower bound prevents micro-contributors from getting disproportionately large allocations, protecting the overall distribution.")

elif st.session_state.current_phase == 3:
    st.markdown("""
    ### The "Preventing Monopolies" Moment
    **Goal:** Show how a **Cap** prevents any single Party from dominating.
    
    A maximum cap limits the share any single country can receive, ensuring the fund is distributed across more participants.
    """)
    
    df = load_data(params)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Allocation Distribution")
        fig_pie = px.pie(df, values='alloc_usd_m', names='party', title="Share of Total Fund")
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        st.subheader("Cap Statistics")
        capped_parties = df[df['share_final'] >= params['cap_share'] * 0.99] # Float precision buffer
        st.metric("Parties at Cap", len(capped_parties))
        if not capped_parties.empty:
            st.write("Parties limited by cap:")
            st.write(", ".join(capped_parties['party'].tolist()))
            
    st.info("**Educational Note:** The Cap prevents any single Party from dominating, ensuring a more proportional distribution among all eligible parties.")

elif st.session_state.current_phase == 4:
    st.markdown("""
    ### The "Supporting the Middle-Income" Moment
    **Goal:** Show how **Baseline Blend** supports least developed and middle-income countries.
    
    Baseline blend allocates a portion of the fund equally among eligible parties, reducing extreme concentration.
    """)
    
    df = load_data(params)
    
    st.subheader("Allocation by Development Status")
    # Handle possible NaN in dev_status
    df['dev_status_filled'] = df['dev_status'].fillna('Other')
    df_dev = df.groupby('dev_status_filled')['alloc_usd_m'].sum().reset_index()
    fig_dev = px.bar(df_dev, x='dev_status_filled', y='alloc_usd_m', color='dev_status_filled', title="Total Allocation by Dev Status")
    st.plotly_chart(fig_dev, use_container_width=True)
    
    st.info("**Educational Note:** Baseline blend reduces concentration and provides a guaranteed minimum for specific categories of countries.")

elif st.session_state.current_phase == 5:
    st.markdown("""
    ### Consolidated Working Model
    **Goal:** Explore all trade-offs in a single view.
    
    Now that you understand each mechanism, you can adjust all parameters to see how they interact.
    """)
    
    df = load_data(params)
    
    # Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Fund", f"${params['fund_usd']/1e9:.1f}B")
    m2.metric("IPLC Envelope", f"${df['iplc_usd_m'].sum():.1f}M")
    m3.metric("State Envelope", f"${df['state_usd_m'].sum():.1f}M")
    m4.metric("Avg Allocation", f"${df['alloc_usd_m'].mean():.2f}M")
    
    st.divider()
    
    # Regional Analysis
    col_reg, col_table = st.columns([1, 1])
    
    with col_reg:
        st.subheader("Allocation by Region")
        df_reg = df.groupby('un_region')['alloc_usd_m'].sum().reset_index()
        fig_reg = px.pie(df_reg, values='alloc_usd_m', names='un_region')
        st.plotly_chart(fig_reg, use_container_width=True)
        
    with col_table:
        st.subheader("Full Results")
        st.dataframe(df[['party', 'un_region', 'dev_status', 'alloc_usd_m']].sort_values('alloc_usd_m', ascending=False), use_container_width=True)

# Navigation buttons
col_prev, col_next = st.columns([1, 1])
with col_prev:
    if st.session_state.current_phase > 0:
        if st.button("⬅️ Previous Phase"):
            st.session_state.current_phase -= 1
            st.rerun()

with col_next:
    if st.session_state.current_phase < len(phases) - 1:
        if st.button("Next Phase ➡️"):
            st.session_state.current_phase += 1
            st.rerun()
