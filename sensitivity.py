from __future__ import annotations

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from logic.calculator import calculate_allocations
from logic.data_loader import get_base_data, load_data
from logic.reporting import (
    generate_comparative_report,
    generate_local_stability_markdown,
    generate_scenario_brief,
    generate_sweep_summary,
    generate_technical_annex,
)
from logic.sensitivity_metrics import (
    build_pure_iusaf_comparator,
    compute_country_deltas,
    compute_local_stability_metrics,
    compute_metrics,
    run_invariant_checks,
    summarize_group_totals,
)
from logic.sensitivity_scenarios import DEFAULT_BASELINE, get_default_ranges, get_scenario_library, one_way_sweep, two_way_grid


st.set_page_config(page_title="Cali Sensitivity Testing", layout="wide")


@st.cache_resource
def load_base_df() -> pd.DataFrame:
    con = duckdb.connect(database=":memory:")
    load_data(con)
    return get_base_data(con)


def run_scenario(base_df: pd.DataFrame, scenario: dict) -> pd.DataFrame:
    return calculate_allocations(
        base_df,
        fund_size=float(scenario["fund_size"]),
        iplc_share_pct=float(scenario["iplc_share_pct"]),
        exclude_high_income=bool(scenario["exclude_high_income"]),
        floor_pct=float(scenario.get("floor_pct", 0.0) or 0.0),
        ceiling_pct=scenario.get("ceiling_pct"),
        tsac_beta=float(scenario.get("tsac_beta", 0.0)),
        sosac_gamma=float(scenario.get("sosac_gamma", 0.0)),
        equality_mode=bool(scenario.get("equality_mode", False)),
        un_scale_mode=scenario.get("un_scale_mode", "band_inversion"),
    )


def with_id(scenario: dict, scenario_id: str) -> dict:
    s = dict(scenario)
    s["scenario_id"] = scenario_id
    return s


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


base_df = load_base_df()
scenario_library = get_scenario_library()
ranges = get_default_ranges()

st.title("Cali Fund Sensitivity Testing and Reporting")
st.caption("Robustness diagnostics and analytical reporting app using the same model logic as the main calculator.")

st.sidebar.header("Scenario Setup")
library_choice = st.sidebar.selectbox("Named scenario", options=list(scenario_library.keys()), index=list(scenario_library.keys()).index("balanced_baseline"))
scenario = dict(scenario_library[library_choice])

scenario["fund_size"] = st.sidebar.selectbox("Fund size anchor", options=ranges["fund_size"], index=ranges["fund_size"].index(scenario.get("fund_size", 1_000_000_000)))
scenario["un_scale_mode"] = st.sidebar.selectbox("UN inversion mode", options=ranges["un_scale_mode"], index=ranges["un_scale_mode"].index(scenario.get("un_scale_mode", "band_inversion")))
scenario["exclude_high_income"] = st.sidebar.checkbox("Exclude high-income (except SIDS)", value=bool(scenario.get("exclude_high_income", True)))
scenario["equality_mode"] = st.sidebar.checkbox("Equality mode", value=bool(scenario.get("equality_mode", False)))
scenario["tsac_beta"] = st.sidebar.slider("TSAC", min_value=0.0, max_value=0.15, step=0.01, value=float(scenario.get("tsac_beta", 0.05)))
scenario["sosac_gamma"] = st.sidebar.slider("SOSAC", min_value=0.0, max_value=0.10, step=0.01, value=float(scenario.get("sosac_gamma", 0.03)))
scenario["iplc_share_pct"] = st.sidebar.selectbox("IPLC share", options=ranges["iplc_share_pct"], index=ranges["iplc_share_pct"].index(int(scenario.get("iplc_share_pct", 50))))
scenario["floor_pct"] = st.sidebar.selectbox("Floor (%)", options=ranges["floor_pct"], index=ranges["floor_pct"].index(float(scenario.get("floor_pct", 0.0) or 0.0)))
scenario["ceiling_pct"] = st.sidebar.selectbox("Ceiling (%)", options=ranges["ceiling_pct"], index=ranges["ceiling_pct"].index(scenario.get("ceiling_pct", None)))

if scenario["tsac_beta"] + scenario["sosac_gamma"] >= 1.0:
    st.sidebar.error("TSAC + SOSAC must stay below 1.0.")
    st.stop()

scenario = with_id(scenario, library_choice)
current_results = run_scenario(base_df, scenario)

pure_iusaf = with_id(build_pure_iusaf_comparator({**DEFAULT_BASELINE, **scenario}, keep_constraints=True), "pure_iusaf_benchmark")
equality = with_id(
    {
        **pure_iusaf,
        "equality_mode": True,
        "scenario_id": "equality_benchmark",
    },
    "equality_benchmark",
)

iusaf_results = run_scenario(base_df, pure_iusaf)
equality_results = run_scenario(base_df, equality)

local_stability_metrics, local_stability_table = compute_local_stability_metrics(
    base_scenario=scenario,
    base_results_df=current_results,
    base_df=base_df,
    run_scenario_fn=run_scenario,
    ranges=ranges,
)

current_metrics = compute_metrics(scenario, current_results, iusaf_results, equality_results, local_stability=local_stability_metrics)
country_deltas = compute_country_deltas(current_results, iusaf_results)
group_summary = summarize_group_totals(current_results)

top_gainers = country_deltas[country_deltas["eligible"]].nlargest(5, "allocation_delta_m")[["party", "allocation_delta_m"]]
top_losers = country_deltas[country_deltas["eligible"]].nsmallest(5, "allocation_delta_m")[["party", "allocation_delta_m"]]

library_metrics = []
for name, s in scenario_library.items():
    scenario_i = dict(s)
    scenario_i["fund_size"] = scenario["fund_size"]
    scenario_i["scenario_id"] = name
    res = run_scenario(base_df, scenario_i)
    comp_s = build_pure_iusaf_comparator(scenario_i, keep_constraints=True)
    baseline_iusaf = run_scenario(base_df, comp_s)
    baseline_eq = run_scenario(base_df, {**comp_s, "equality_mode": True, "scenario_id": f"{name}_eq"})
    local_i, _ = compute_local_stability_metrics(
        base_scenario=scenario_i,
        base_results_df=res,
        base_df=base_df,
        run_scenario_fn=run_scenario,
        ranges=ranges,
    )
    library_metrics.append(compute_metrics(scenario_i, res, baseline_iusaf, baseline_eq, local_stability=local_i))

library_metrics_df = pd.DataFrame(library_metrics)

tab1, tab2, tab3, tab4 = st.tabs(["Parameter Sweep", "Robustness Diagnostics", "Thresholds and Tipping Points", "Attack Surface Report"])

with tab1:
    st.subheader("Single Scenario")
    box1, box2 = st.columns(2)
    with box1:
        st.info(
            f"Overlay Strength vs Pure IUSAF: **{current_metrics['overlay_strength_label']}**\n\n"
            f"Spearman={current_metrics['spearman_vs_pure_iusaf']:.4f}, Top20 turnover={current_metrics['top20_turnover_vs_pure_iusaf']:.1%}"
        )
    with box2:
        level = current_metrics.get("local_stability_label", "not_evaluated")
        message = (
            f"Local Stability Around Blended Baseline: **{level}**\n\n"
            f"Local min Spearman={current_metrics.get('local_min_spearman_vs_baseline', float('nan')):.4f}, "
            f"Local max turnover={current_metrics.get('local_max_top20_turnover_vs_baseline', float('nan')):.1%}"
        )
        if current_metrics.get("local_blended_instability_flag", False):
            st.warning(message)
        else:
            st.success(message)

    st.dataframe(pd.DataFrame([current_metrics]))

    st.markdown("### Local stability checks")
    st.dataframe(
        local_stability_table[
            [
                "parameter_changed",
                "new_value",
                "spearman_vs_baseline",
                "top20_turnover_vs_baseline",
                "mean_abs_share_delta_vs_baseline",
            ]
        ]
        if not local_stability_table.empty
        else local_stability_table
    )
    st.markdown(
        f"This scenario differs from pure IUSAF because stewardship overlays are active. "
        f"However, nearby parameter changes indicate that the blended model is **{current_metrics.get('local_stability_label', 'not_evaluated')}**."
    )

    st.subheader("One-way Sweep")
    one_way_param = st.selectbox("Parameter", options=["tsac_beta", "sosac_gamma", "iplc_share_pct", "floor_pct", "ceiling_pct", "fund_size"], index=0)
    one_way_values = ranges[one_way_param]
    one_way_scenarios = one_way_sweep(scenario, one_way_param, one_way_values)
    one_way_metrics = []
    for s in one_way_scenarios:
        res = run_scenario(base_df, s)
        comp_s = build_pure_iusaf_comparator(s, keep_constraints=True)
        iusaf_ref = run_scenario(base_df, comp_s)
        eq_ref = run_scenario(base_df, {**comp_s, "equality_mode": True, "scenario_id": f"{s.get('scenario_id')}_eq"})
        one_way_metrics.append(compute_metrics(s, res, iusaf_ref, eq_ref))
    one_way_df = pd.DataFrame(one_way_metrics)
    st.dataframe(one_way_df[["scenario_id", "spearman_vs_pure_iusaf", "top20_turnover_vs_pure_iusaf", "overlay_strength_label", "departure_from_pure_iusaf_flag"]])

    tornado_df = one_way_df[["scenario_id", "spearman_vs_pure_iusaf"]].copy()
    tornado_df["impact"] = (1 - tornado_df["spearman_vs_pure_iusaf"]).abs()
    st.plotly_chart(px.bar(tornado_df, x="scenario_id", y="impact", title="Tornado-style one-way impact (1 - Spearman)") , use_container_width=True)

    st.subheader("Two-way Grid Sweep")
    grid_choice = st.selectbox("Grid", options=["TSAC × SOSAC", "Floor × Ceiling", "UN mode × TSAC", "UN mode × SOSAC", "Exclude-HI × TSAC"])
    if grid_choice == "TSAC × SOSAC":
        grid_scenarios = two_way_grid(scenario, "tsac_beta", ranges["tsac_beta"], "sosac_gamma", ranges["sosac_gamma"], "tsac_sosac")
        x_col, y_col = "tsac_beta", "sosac_gamma"
    elif grid_choice == "Floor × Ceiling":
        grid_scenarios = two_way_grid(scenario, "floor_pct", ranges["floor_pct"], "ceiling_pct", ranges["ceiling_pct"], "floor_ceiling")
        x_col, y_col = "floor_pct", "ceiling_pct"
    elif grid_choice == "UN mode × TSAC":
        grid_scenarios = two_way_grid(scenario, "un_scale_mode", ranges["un_scale_mode"], "tsac_beta", ranges["tsac_beta"], "unmode_tsac")
        x_col, y_col = "un_scale_mode", "tsac_beta"
    elif grid_choice == "UN mode × SOSAC":
        grid_scenarios = two_way_grid(scenario, "un_scale_mode", ranges["un_scale_mode"], "sosac_gamma", ranges["sosac_gamma"], "unmode_sosac")
        x_col, y_col = "un_scale_mode", "sosac_gamma"
    else:
        grid_scenarios = two_way_grid(scenario, "exclude_high_income", ranges["exclude_high_income"], "tsac_beta", ranges["tsac_beta"], "exclude_tsac")
        x_col, y_col = "exclude_high_income", "tsac_beta"

    grid_metrics = []
    for s in grid_scenarios:
        res = run_scenario(base_df, s)
        comp_s = build_pure_iusaf_comparator(s, keep_constraints=True)
        iusaf_ref = run_scenario(base_df, comp_s)
        eq_ref = run_scenario(base_df, {**comp_s, "equality_mode": True, "scenario_id": f"{s.get('scenario_id')}_eq"})
        grid_metrics.append(compute_metrics(s, res, iusaf_ref, eq_ref))
    grid_df = pd.DataFrame(grid_metrics)

    heat_metric = st.selectbox("Heatmap metric", options=["spearman_vs_pure_iusaf", "pct_below_equality", "sids_total", "hhi", "top20_turnover_vs_pure_iusaf"], index=0)
    pivot = grid_df.pivot_table(index=y_col, columns=x_col, values=heat_metric, aggfunc="mean")
    st.plotly_chart(px.imshow(pivot, aspect="auto", title=f"{grid_choice} heatmap: {heat_metric}", labels={"x": x_col, "y": y_col, "color": heat_metric}), use_container_width=True)

    st.markdown(
        "## Interpretation\n"
        "### 1. Mechanical validity\n"
        "Sweep results are interpreted only when conservation and non-negativity checks hold.\n\n"
        "### 2. Relationship to pure IUSAF\n"
        f"The one-way and grid views quantify policy-overlay departure using `{one_way_param}` and pure-IUSAF comparators. This departure is expected when stewardship overlays are active.\n\n"
        "### 3. Stability of the blended specification\n"
        "Local stability is assessed separately via adjacent-parameter checks rather than pure-IUSAF divergence alone.\n\n"
        "### 4. Distributional implications\n"
        "Heatmap regions with high turnover or high equality-distance indicate where distributional effects become more pronounced.\n\n"
        "### 5. Caveats\n"
        "Departure from pure IUSAF should not be read as fragility unless local instability diagnostics also indicate excessive sensitivity."
    )

with tab2:
    st.subheader("Invariant and Edge-case Diagnostics")
    no_sids_df = base_df.copy()
    no_sids_df["is_sids"] = False
    no_sids_results = run_scenario(no_sids_df, scenario)
    diag_df = run_invariant_checks(scenario, current_results, no_sids_results_df=no_sids_results)
    st.dataframe(diag_df)

    binding_df = pd.DataFrame(
        {
            "constraint": ["floor_binding_count", "ceiling_binding_count"],
            "count": [current_metrics["floor_binding_count"], current_metrics["ceiling_binding_count"]],
        }
    )
    st.plotly_chart(px.bar(binding_df, x="constraint", y="count", title="Floor/Ceiling binding counts"), use_container_width=True)

    st.markdown(
        "## Interpretation\n"
        "### 1. Mechanical validity\n"
        "Diagnostics indicate whether conservation, normalization, and fallback logic hold for the selected scenario.\n\n"
        "### 2. Relationship to pure IUSAF\n"
        "These checks do not measure policy-overlay departure; that is reported separately in pure-IUSAF comparator metrics.\n\n"
        "### 3. Stability of the blended specification\n"
        "Constraint binding can contribute to local sensitivity and should be read with local stability checks.\n\n"
        "### 4. Distributional implications\n"
        "Higher floor/ceiling binding counts imply stronger shape effects on allocation distribution.\n\n"
        "### 5. Caveats\n"
        "Mechanical validity is necessary but not sufficient for robustness conclusions."
    )

with tab3:
    st.subheader("Threshold and Tipping Point Analysis")
    threshold_df = library_metrics_df[["scenario_id", "tsac_beta", "sosac_gamma", "spearman_vs_pure_iusaf", "top20_turnover_vs_pure_iusaf", "pct_below_equality", "departure_from_pure_iusaf_flag", "local_blended_instability_flag"]].copy()
    threshold_df["stewardship_total"] = threshold_df["tsac_beta"] + threshold_df["sosac_gamma"]
    threshold_df = threshold_df.sort_values("stewardship_total")

    st.plotly_chart(
        px.line(
            threshold_df,
            x="stewardship_total",
            y="spearman_vs_pure_iusaf",
            color="departure_from_pure_iusaf_flag",
            markers=True,
            title="Threshold chart: stewardship total vs pure-IUSAF departure",
        ),
        use_container_width=True,
    )

    rank_plot_df = one_way_df[["scenario_id", "spearman_vs_pure_iusaf", "top20_turnover_vs_pure_iusaf"]].copy()
    st.plotly_chart(px.scatter(rank_plot_df, x="top20_turnover_vs_pure_iusaf", y="spearman_vs_pure_iusaf", text="scenario_id", title="Pure-IUSAF departure plot"), use_container_width=True)

    st.markdown(
        "## Interpretation\n"
        "### 1. Mechanical validity\n"
        "Threshold signals are interpreted only for scenarios that pass invariant checks.\n\n"
        "### 2. Relationship to pure IUSAF\n"
        "The line chart shows where overlay departure thresholds are crossed; this captures policy departure strength rather than instability.\n\n"
        "### 3. Stability of the blended specification\n"
        "Local blended instability is flagged separately and should be used for robustness conclusions.\n\n"
        "### 4. Distributional implications\n"
        "Departure and instability flags together identify where ranking and concentration changes become politically material.\n\n"
        "### 5. Caveats\n"
        "A strong overlay can still be locally stable; avoid conflating these two diagnostics."
    )

with tab4:
    st.subheader("Attack Surface Analysis")
    attack_rows = []
    attack_rows.append(
        {
            "critique": "TSAC/SOSAC defeat base model",
            "evidence": f"Overlay vs pure IUSAF: Spearman={current_metrics['spearman_vs_pure_iusaf']:.4f}, turnover={current_metrics['top20_turnover_vs_pure_iusaf']:.1%}, label={current_metrics['overlay_strength_label']}",
        }
    )
    raw = library_metrics_df[library_metrics_df["scenario_id"] == "pure_iusaf_raw"]
    band = library_metrics_df[library_metrics_df["scenario_id"] == "pure_iusaf_band"]
    if not raw.empty and not band.empty:
        attack_rows.append(
            {
                "critique": "Band inversion is arbitrary",
                "evidence": f"Raw/Band HHI: {raw.iloc[0]['hhi']:.4f} / {band.iloc[0]['hhi']:.4f}; top20 share: {raw.iloc[0]['top20_share']:.2%} / {band.iloc[0]['top20_share']:.2%}",
            }
        )
    attack_rows.append(
        {
            "critique": "Floor and ceiling are doing the real work",
            "evidence": f"Bound countries: floor={current_metrics['floor_binding_count']}, ceiling={current_metrics['ceiling_binding_count']}",
        }
    )
    attack_rows.append(
        {
            "critique": "Excluding high-income countries determines result",
            "evidence": "Compare `exclude_hi_on_compare` vs `exclude_hi_off_compare` in scenario metrics export.",
        }
    )
    attack_rows.append(
        {
            "critique": "SOSAC is a political subsidy",
            "evidence": f"SIDS totals across library range from {library_metrics_df['sids_total'].min():.2f}m to {library_metrics_df['sids_total'].max():.2f}m.",
        }
    )
    st.dataframe(pd.DataFrame(attack_rows))

    scenario_brief_md = generate_scenario_brief(current_metrics, top_gainers, top_losers)
    sweep_summary_md = generate_sweep_summary("one-way sweep", one_way_df, "spearman_vs_pure_iusaf")
    comparative_md = generate_comparative_report(library_metrics_df, baseline_id="balanced_baseline")
    annex_md = generate_technical_annex()
    local_stability_md = generate_local_stability_markdown(current_metrics, local_stability_table)

    st.markdown("## Interpretation")
    st.markdown(
        "### 1. Mechanical validity\n"
        "This section assumes scenarios are mechanically valid and reproducible under shared model logic.\n\n"
        "### 2. Relationship to pure IUSAF\n"
        "Departure metrics capture intended stewardship overlay effects and are not interpreted as fragility by default.\n\n"
        "### 3. Stability of the blended specification\n"
        "Local stability diagnostics indicate whether nearby parameter changes create bounded or excessive shifts.\n\n"
        "### 4. Distributional implications\n"
        "Country-level and group-level deltas are used to describe gainers, losers, and concentration effects.\n\n"
        "### 5. Caveats\n"
        "Robustness conclusions should rely on local-stability evidence, not pure-IUSAF departure alone."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download Scenario Brief (.md)", scenario_brief_md, file_name="scenario_brief.md")
        st.download_button("Download Sweep Summary (.md)", sweep_summary_md, file_name="sweep_summary.md")
        st.download_button("Download Local Stability Narrative (.md)", local_stability_md, file_name="local_stability.md")
    with c2:
        st.download_button("Download Comparative Report (.md)", comparative_md, file_name="comparative_report.md")
        st.download_button("Download Technical Annex (.md)", annex_md, file_name="technical_annex.md")

st.divider()
st.subheader("Data Exports")
e1, e2, e3, e4, e5 = st.columns(5)
with e1:
    st.download_button("Scenario metrics CSV", csv_bytes(library_metrics_df), file_name="scenario_metrics.csv", mime="text/csv")
with e2:
    st.download_button("Country results CSV", csv_bytes(current_results), file_name="country_results.csv", mime="text/csv")
with e3:
    st.download_button("Country deltas CSV", csv_bytes(country_deltas), file_name="country_deltas.csv", mime="text/csv")
with e4:
    st.download_button("Group summary CSV", csv_bytes(group_summary), file_name="group_summary.csv", mime="text/csv")
with e5:
    st.download_button("Local stability checks CSV", csv_bytes(local_stability_table), file_name="local_stability_checks.csv", mime="text/csv")
