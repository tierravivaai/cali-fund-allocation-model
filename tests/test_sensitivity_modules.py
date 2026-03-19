import duckdb

from logic.calculator import calculate_allocations
from logic.data_loader import get_base_data, load_data
from logic.reporting import classify_local_stability, classify_overlay_strength
from logic.sensitivity_metrics import compute_local_stability_metrics, compute_metrics, run_invariant_checks
from logic.sensitivity_scenarios import get_scenario_library


def _base_df():
    con = duckdb.connect(database=":memory:")
    load_data(con)
    return get_base_data(con)


def test_scenario_library_contains_required_entries():
    library = get_scenario_library()
    required = {
        "pure_equality",
        "pure_iusaf_raw",
        "pure_iusaf_band",
        "balanced_baseline",
        "balanced_5_3",
        "terrestrial_max",
        "ocean_max",
        "balanced_floor_005",
        "balanced_ceiling_1",
        "balanced_floor_005_ceiling_1",
        "exclude_hi_off_compare",
        "exclude_hi_on_compare",
        "raw_vs_band_compare",
    }
    assert required.issubset(set(library.keys()))


def test_metrics_and_invariants_run_for_balanced_baseline():
    df = _base_df()
    scenario = get_scenario_library()["balanced_baseline"]
    current = calculate_allocations(df, scenario["fund_size"], scenario["iplc_share_pct"], exclude_high_income=scenario["exclude_high_income"], floor_pct=scenario["floor_pct"], ceiling_pct=scenario["ceiling_pct"], tsac_beta=scenario["tsac_beta"], sosac_gamma=scenario["sosac_gamma"], equality_mode=scenario["equality_mode"], un_scale_mode=scenario["un_scale_mode"])
    iusaf = calculate_allocations(df, scenario["fund_size"], scenario["iplc_share_pct"], exclude_high_income=scenario["exclude_high_income"], tsac_beta=0.0, sosac_gamma=0.0, equality_mode=False, un_scale_mode=scenario["un_scale_mode"])
    equality = calculate_allocations(df, scenario["fund_size"], scenario["iplc_share_pct"], exclude_high_income=scenario["exclude_high_income"], tsac_beta=0.0, sosac_gamma=0.0, equality_mode=True, un_scale_mode=scenario["un_scale_mode"])

    local, _ = compute_local_stability_metrics(
        base_scenario=scenario,
        base_results_df=current,
        base_df=df,
        run_scenario_fn=lambda _df, s: calculate_allocations(
            _df,
            s["fund_size"],
            s["iplc_share_pct"],
            exclude_high_income=s["exclude_high_income"],
            floor_pct=s["floor_pct"],
            ceiling_pct=s["ceiling_pct"],
            tsac_beta=s["tsac_beta"],
            sosac_gamma=s["sosac_gamma"],
            equality_mode=s["equality_mode"],
            un_scale_mode=s["un_scale_mode"],
        ),
    )

    metrics = compute_metrics(scenario, current, iusaf, equality, local_stability=local)
    assert metrics["n_eligible"] > 0
    assert abs(metrics["sum_final_share"] - 1.0) < 1e-6
    assert "overlay_strength_label" in metrics
    assert "local_stability_label" in metrics
    assert "departure_from_pure_iusaf_flag" in metrics
    assert "local_blended_instability_flag" in metrics

    checks = run_invariant_checks(scenario, current)
    assert checks["pass"].all()


def test_overlay_and_local_stability_are_distinct_concepts():
    assert classify_overlay_strength(0.92, 0.15) == "strong overlay"
    assert classify_local_stability(0.995, 0.03) == "stable"
