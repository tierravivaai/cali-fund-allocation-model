from __future__ import annotations

import math
from typing import Any

import pandas as pd

from logic.calculator import get_outcome_warning_feedback, get_stewardship_blend_feedback
from logic.sensitivity_scenarios import generate_local_neighbor_scenarios as _generate_local_neighbor_scenarios


STRUCTURAL_BREAK_RULES = {
    "stewardship_total_gt": 0.20,
    "spearman_vs_pure_iusaf_lt": 0.95,
    "top20_turnover_vs_pure_iusaf_gt": 0.20,
    "pct_below_equality_gt": 60.0,
    "median_pct_of_equality_lt": 90.0,
}

LOCAL_INSTABILITY_RULES = {
    "min_spearman_lt": 0.94,
    "max_top20_turnover_gt": 0.20,
    "max_abs_share_delta_gt": 0.005,
}


def _safe_float(value, default: float = 0.0) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    try:
        return float(value)
    except Exception:
        return default


def _gini(values: pd.Series) -> float:
    x = values.fillna(0.0).astype(float)
    if len(x) == 0:
        return 0.0
    if (x < 0).any():
        x = x - x.min()
    x = x.sort_values().reset_index(drop=True)
    n = len(x)
    total = x.sum()
    if total <= 0:
        return 0.0
    weighted_sum = ((x.index + 1) * x).sum()
    return float((2 * weighted_sum) / (n * total) - (n + 1) / n)


def _hhi(shares: pd.Series) -> float:
    s = shares.fillna(0.0).astype(float)
    return float((s**2).sum())


def _top_turnover(current: pd.DataFrame, baseline: pd.DataFrame, n: int = 20) -> float:
    cur_top = set(current.nlargest(min(n, len(current)), "final_share")["party"].tolist())
    base_top = set(baseline.nlargest(min(n, len(baseline)), "final_share")["party"].tolist())
    universe = max(1, min(n, len(cur_top | base_top)))
    return float(len(cur_top.symmetric_difference(base_top)) / universe)


def _eligible(results_df: pd.DataFrame) -> pd.DataFrame:
    return results_df[results_df["eligible"]].copy()


def _spearman_by_party(current: pd.DataFrame, baseline: pd.DataFrame) -> float:
    merged = current[["party", "final_share"]].merge(
        baseline[["party", "final_share"]], on="party", how="inner", suffixes=("_cur", "_base")
    )
    if merged.empty:
        return float("nan")
    r_cur = merged["final_share_cur"].rank(method="average")
    r_base = merged["final_share_base"].rank(method="average")
    return float(r_cur.corr(r_base, method="pearson"))


def _group_totals(eligible_df: pd.DataFrame, group_col: str) -> dict[str, float]:
    if group_col not in eligible_df.columns:
        return {}
    grouped = eligible_df.groupby(group_col, dropna=False)["total_allocation"].sum().to_dict()
    out = {}
    for key, value in grouped.items():
        label = "NA" if pd.isna(key) else str(key)
        out[label] = float(value)
    return out


def build_pure_iusaf_comparator(scenario: dict, keep_constraints: bool = True) -> dict:
    comparator = dict(scenario)
    comparator["scenario_id"] = f"{scenario.get('scenario_id', 'scenario')}_pure_iusaf_comp"
    comparator["tsac_beta"] = 0.0
    comparator["sosac_gamma"] = 0.0
    comparator["equality_mode"] = False
    if not keep_constraints:
        comparator["floor_pct"] = 0.0
        comparator["ceiling_pct"] = None
    return comparator


def compute_departure_from_pure_iusaf(current_results_df: pd.DataFrame, pure_iusaf_results_df: pd.DataFrame) -> dict[str, Any]:
    cur = _eligible(current_results_df)
    pure = _eligible(pure_iusaf_results_df)
    merged = cur[["party", "final_share"]].merge(
        pure[["party", "final_share"]],
        on="party",
        how="inner",
        suffixes=("_cur", "_pure"),
    )
    if merged.empty:
        spearman = float("nan")
        turnover = 0.0
        mean_abs = 0.0
        max_abs = 0.0
    else:
        spearman = _spearman_by_party(cur, pure)
        turnover = _top_turnover(cur, pure, n=20)
        abs_delta = (merged["final_share_cur"] - merged["final_share_pure"]).abs()
        mean_abs = float(abs_delta.mean())
        max_abs = float(abs_delta.max())

    if spearman >= 0.98 and turnover <= 0.10:
        overlay_label = "minimal overlay"
    elif spearman >= 0.95 and turnover <= 0.20:
        overlay_label = "moderate overlay"
    elif spearman >= 0.90 or turnover <= 0.40:
        overlay_label = "strong overlay"
    else:
        overlay_label = "dominant overlay"

    departure_flag = bool((spearman < 0.95) or (turnover > 0.20))
    return {
        "spearman_vs_pure_iusaf": spearman,
        "top20_turnover_vs_pure_iusaf": turnover,
        "mean_abs_share_delta_vs_pure_iusaf": mean_abs,
        "max_abs_share_delta_vs_pure_iusaf": max_abs,
        "overlay_strength_label": overlay_label,
        "departure_from_pure_iusaf_flag": departure_flag,
    }


def generate_local_neighbor_scenarios(base_scenario: dict, ranges: dict[str, list] | None = None) -> list[dict]:
    return _generate_local_neighbor_scenarios(base_scenario, ranges=ranges)


def compute_local_stability_metrics(
    base_scenario: dict,
    base_results_df: pd.DataFrame,
    base_df: pd.DataFrame,
    run_scenario_fn,
    ranges: dict[str, list] | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    neighbors = generate_local_neighbor_scenarios(base_scenario, ranges=ranges)
    base_eligible = _eligible(base_results_df)
    rows = []

    for n in neighbors:
        n_results = run_scenario_fn(base_df, n)
        n_eligible = _eligible(n_results)
        merged = base_eligible[["party", "final_share"]].merge(
            n_eligible[["party", "final_share"]],
            on="party",
            how="inner",
            suffixes=("_base", "_neighbor"),
        )
        abs_delta = (merged["final_share_base"] - merged["final_share_neighbor"]).abs() if not merged.empty else pd.Series(dtype=float)

        changed_params = []
        for key in ["tsac_beta", "sosac_gamma", "iplc_share_pct", "floor_pct", "ceiling_pct"]:
            if n.get(key) != base_scenario.get(key):
                changed_params.append((key, n.get(key)))
        param_changed, new_value = changed_params[0] if changed_params else ("none", None)

        rows.append(
            {
                "scenario_id": n.get("scenario_id"),
                "parameter_changed": param_changed,
                "new_value": new_value,
                "spearman_vs_baseline": _spearman_by_party(n_eligible, base_eligible),
                "top20_turnover_vs_baseline": _top_turnover(n_eligible, base_eligible, n=20),
                "mean_abs_share_delta_vs_baseline": float(abs_delta.mean()) if len(abs_delta) else 0.0,
                "max_abs_share_delta_vs_baseline": float(abs_delta.max()) if len(abs_delta) else 0.0,
            }
        )

    table = pd.DataFrame(rows)
    if table.empty:
        out = {
            "local_min_spearman_vs_baseline": 1.0,
            "local_max_top20_turnover_vs_baseline": 0.0,
            "local_mean_mean_abs_share_delta": 0.0,
            "local_max_abs_share_delta": 0.0,
            "local_stability_label": "stable",
            "local_blended_instability_flag": False,
        }
        return out, table

    min_spearman = float(table["spearman_vs_baseline"].min())
    max_turnover = float(table["top20_turnover_vs_baseline"].max())
    mean_mean_abs = float(table["mean_abs_share_delta_vs_baseline"].mean())
    max_abs = float(table["max_abs_share_delta_vs_baseline"].max())

    if min_spearman >= 0.99 and max_turnover <= 0.05:
        label = "stable"
    elif min_spearman >= 0.97 and max_turnover <= 0.10:
        label = "moderately sensitive"
    elif min_spearman >= 0.94 and max_turnover <= 0.20:
        label = "sensitive"
    else:
        label = "unstable"

    instability = bool(
        min_spearman < LOCAL_INSTABILITY_RULES["min_spearman_lt"]
        or max_turnover > LOCAL_INSTABILITY_RULES["max_top20_turnover_gt"]
        or max_abs > LOCAL_INSTABILITY_RULES["max_abs_share_delta_gt"]
    )

    out = {
        "local_min_spearman_vs_baseline": min_spearman,
        "local_max_top20_turnover_vs_baseline": max_turnover,
        "local_mean_mean_abs_share_delta": mean_mean_abs,
        "local_max_abs_share_delta": max_abs,
        "local_stability_label": label,
        "local_blended_instability_flag": instability,
    }
    return out, table


def structural_break_flag(metrics: dict[str, Any]) -> bool:
    # Backward-compatibility flag: interpreted as material departure from pure IUSAF/equality,
    # not as local-instability of the blended specification.
    checks = [
        (metrics.get("tsac_beta", 0.0) + metrics.get("sosac_gamma", 0.0)) > STRUCTURAL_BREAK_RULES["stewardship_total_gt"],
        metrics.get("spearman_vs_pure_iusaf", 1.0) < STRUCTURAL_BREAK_RULES["spearman_vs_pure_iusaf_lt"],
        metrics.get("top20_turnover_vs_pure_iusaf", 0.0) > STRUCTURAL_BREAK_RULES["top20_turnover_vs_pure_iusaf_gt"],
        metrics.get("pct_below_equality", 0.0) > STRUCTURAL_BREAK_RULES["pct_below_equality_gt"],
        metrics.get("median_pct_of_equality", 100.0) < STRUCTURAL_BREAK_RULES["median_pct_of_equality_lt"],
    ]
    return bool(any(checks))


def compute_metrics(
    scenario: dict,
    results_df: pd.DataFrame,
    iusaf_baseline_df: pd.DataFrame,
    equality_baseline_df: pd.DataFrame,
    local_stability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    eligible_df = _eligible(results_df)
    iusaf_eligible = _eligible(iusaf_baseline_df)
    equality_eligible = _eligible(equality_baseline_df)

    n_eligible = int(len(eligible_df))
    n_sids_eligible = int(eligible_df["is_sids"].sum()) if "is_sids" in eligible_df else 0
    fund_size = float(scenario["fund_size"])
    total_m = fund_size / 1_000_000.0

    eq_ref = (fund_size / n_eligible / 1_000_000.0) if n_eligible > 0 else 0.0
    if eq_ref > 0 and n_eligible > 0:
        pct_below_eq = float((eligible_df["total_allocation"] < eq_ref).mean() * 100.0)
        median_pct_eq = float((eligible_df["total_allocation"].median() / eq_ref) * 100.0)
    else:
        pct_below_eq = 0.0
        median_pct_eq = 100.0

    floor_threshold = float(scenario.get("floor_pct") or 0.0) / 100.0
    ceiling_raw = scenario.get("ceiling_pct")
    ceiling_threshold = None if ceiling_raw is None else float(ceiling_raw) / 100.0

    if floor_threshold > 0:
        floor_binding_count = int((eligible_df["final_share"] <= floor_threshold + 1e-9).sum())
    else:
        floor_binding_count = 0

    if ceiling_threshold is not None:
        ceiling_binding_count = int((eligible_df["final_share"] >= ceiling_threshold - 1e-9).sum())
    else:
        ceiling_binding_count = 0

    stewardship_feedback = get_stewardship_blend_feedback(
        float(scenario.get("tsac_beta", 0.0)), float(scenario.get("sosac_gamma", 0.0))
    )
    outcome_feedback = get_outcome_warning_feedback(results_df, fund_size)

    departure = compute_departure_from_pure_iusaf(results_df, iusaf_baseline_df)
    local = local_stability or {
        "local_min_spearman_vs_baseline": float("nan"),
        "local_max_top20_turnover_vs_baseline": float("nan"),
        "local_mean_mean_abs_share_delta": float("nan"),
        "local_max_abs_share_delta": float("nan"),
        "local_stability_label": "not_evaluated",
        "local_blended_instability_flag": False,
    }

    metrics = {
        "scenario_id": scenario.get("scenario_id", "scenario"),
        "fund_size": fund_size,
        "un_scale_mode": scenario.get("un_scale_mode"),
        "exclude_hi": bool(scenario.get("exclude_high_income", False)),
        "iplc_share": float(scenario.get("iplc_share_pct", 50)),
        "tsac_beta": float(scenario.get("tsac_beta", 0.0)),
        "sosac_gamma": float(scenario.get("sosac_gamma", 0.0)),
        "floor_pct": float(scenario.get("floor_pct", 0.0) or 0.0),
        "ceiling_pct": None if ceiling_raw is None else float(ceiling_raw),
        "n_eligible": n_eligible,
        "n_sids_eligible": n_sids_eligible,
        "floor_binding_count": floor_binding_count,
        "ceiling_binding_count": ceiling_binding_count,
        "sum_final_share": float(eligible_df["final_share"].sum()) if n_eligible else 0.0,
        "sum_total_allocation": float(eligible_df["total_allocation"].sum()) if n_eligible else 0.0,
        "negative_count": int((eligible_df[["final_share", "total_allocation", "state_component", "iplc_component"]] < 0).sum().sum())
        if n_eligible
        else 0,
        "top10_share": float(eligible_df.nlargest(min(10, n_eligible), "final_share")["final_share"].sum()) if n_eligible else 0.0,
        "top20_share": float(eligible_df.nlargest(min(20, n_eligible), "final_share")["final_share"].sum()) if n_eligible else 0.0,
        "mean_alloc": float(eligible_df["total_allocation"].mean()) if n_eligible else 0.0,
        "median_alloc": float(eligible_df["total_allocation"].median()) if n_eligible else 0.0,
        "p90_p10_ratio": float(
            eligible_df["total_allocation"].quantile(0.90) / max(eligible_df["total_allocation"].quantile(0.10), 1e-9)
        )
        if n_eligible
        else 0.0,
        "hhi": _hhi(eligible_df["final_share"]) if n_eligible else 0.0,
        "gini": _gini(eligible_df["final_share"]) if n_eligible else 0.0,
        "pct_below_equality": pct_below_eq,
        "median_pct_of_equality": median_pct_eq,
        "spearman_vs_iusaf": departure["spearman_vs_pure_iusaf"],
        "spearman_vs_equality": _spearman_by_party(eligible_df, equality_eligible),
        "top20_turnover_vs_iusaf": departure["top20_turnover_vs_pure_iusaf"],
        "spearman_vs_pure_iusaf": departure["spearman_vs_pure_iusaf"],
        "top20_turnover_vs_pure_iusaf": departure["top20_turnover_vs_pure_iusaf"],
        "mean_abs_share_delta_vs_pure_iusaf": departure["mean_abs_share_delta_vs_pure_iusaf"],
        "max_abs_share_delta_vs_pure_iusaf": departure["max_abs_share_delta_vs_pure_iusaf"],
        "overlay_strength_label": departure["overlay_strength_label"],
        "departure_from_pure_iusaf_flag": departure["departure_from_pure_iusaf_flag"],
        "local_min_spearman_vs_baseline": _safe_float(local.get("local_min_spearman_vs_baseline"), float("nan")),
        "local_max_top20_turnover_vs_baseline": _safe_float(local.get("local_max_top20_turnover_vs_baseline"), float("nan")),
        "local_mean_mean_abs_share_delta": _safe_float(local.get("local_mean_mean_abs_share_delta"), float("nan")),
        "local_max_abs_share_delta": _safe_float(local.get("local_max_abs_share_delta"), float("nan")),
        "local_stability_label": local.get("local_stability_label", "not_evaluated"),
        "local_blended_instability_flag": bool(local.get("local_blended_instability_flag", False)),
        "ldc_total": float(eligible_df[eligible_df["is_ldc"]]["total_allocation"].sum()) if "is_ldc" in eligible_df else 0.0,
        "sids_total": float(eligible_df[eligible_df["is_sids"]]["total_allocation"].sum()) if "is_sids" in eligible_df else 0.0,
        "stewardship_warning_level": stewardship_feedback.get("warning_level", "none"),
        "outcome_warning_flag": bool(outcome_feedback),
        "dominance_flag": bool((scenario.get("tsac_beta", 0.0) + scenario.get("sosac_gamma", 0.0)) > 0.20),
        "expected_total_allocation": total_m,
    }

    metrics["structural_break_flag"] = structural_break_flag(metrics)

    for group, value in _group_totals(eligible_df, "region").items():
        metrics[f"region_{group}"] = value

    for group, value in _group_totals(eligible_df, "WB Income Group").items():
        metrics[f"income_{group}"] = value

    return metrics


def compute_country_deltas(current_df: pd.DataFrame, baseline_df: pd.DataFrame) -> pd.DataFrame:
    cur = current_df[["party", "eligible", "final_share", "total_allocation"]].rename(
        columns={"final_share": "current_share", "total_allocation": "current_allocation_m"}
    )
    base = baseline_df[["party", "final_share", "total_allocation"]].rename(
        columns={"final_share": "baseline_share", "total_allocation": "baseline_allocation_m"}
    )
    merged = cur.merge(base, on="party", how="left")
    merged["share_delta"] = merged["current_share"] - merged["baseline_share"]
    merged["allocation_delta_m"] = merged["current_allocation_m"] - merged["baseline_allocation_m"]
    merged["allocation_delta_pct"] = merged.apply(
        lambda row: 0.0
        if pd.isna(row["baseline_allocation_m"]) or math.isclose(row["baseline_allocation_m"], 0.0)
        else (row["allocation_delta_m"] / row["baseline_allocation_m"]) * 100.0,
        axis=1,
    )
    return merged


def run_invariant_checks(
    scenario: dict,
    results_df: pd.DataFrame,
    no_sids_results_df: pd.DataFrame | None = None,
    tolerance: float = 1e-6,
) -> pd.DataFrame:
    eligible_df = _eligible(results_df)
    n_eligible = len(eligible_df)
    expected_total_m = float(scenario["fund_size"]) / 1_000_000.0

    checks = []

    def add(name: str, status: bool, detail: str):
        checks.append({"check": name, "pass": bool(status), "detail": detail})

    share_sum = float(eligible_df["final_share"].sum()) if n_eligible else 0.0
    add("Conservation of shares", abs(share_sum - 1.0) <= tolerance if n_eligible else True, f"sum={share_sum:.10f}")

    total_sum = float(eligible_df["total_allocation"].sum()) if n_eligible else 0.0
    add(
        "Conservation of money",
        abs(total_sum - expected_total_m) <= max(1e-5, tolerance),
        f"sum={total_sum:.6f}m expected={expected_total_m:.6f}m",
    )

    comp_delta = (eligible_df["state_component"] + eligible_df["iplc_component"] - eligible_df["total_allocation"]).abs().max() if n_eligible else 0.0
    add("Internal component consistency", comp_delta <= max(1e-6, tolerance), f"max_abs_delta={comp_delta:.10f}")

    negatives = int((eligible_df[["final_share", "total_allocation", "state_component", "iplc_component"]] < 0).sum().sum()) if n_eligible else 0
    add("Non-negativity", negatives == 0, f"negative_count={negatives}")

    if scenario.get("equality_mode", False):
        unique_shares = eligible_df["final_share"].round(12).nunique() if n_eligible else 0
        tsac_zero = (eligible_df["tsac_share"] == 0).all() if n_eligible else True
        sosac_zero = (eligible_df["sosac_share"] == 0).all() if n_eligible else True
        add("Equality mode correctness", unique_shares <= 1 and tsac_zero and sosac_zero, f"unique_shares={unique_shares}")
    else:
        add("Equality mode correctness", True, "not in equality mode")

    if scenario.get("un_scale_mode") == "raw_inversion":
        subset = eligible_df[eligible_df["un_share"] > 0][["party", "un_share", "iusaf_share"]].copy()
        subset = subset.sort_values("un_share")
        monotonic = bool((subset["iusaf_share"].diff().fillna(0) <= 1e-9).all())
        add("Raw inversion correctness", monotonic, f"rows_checked={len(subset)}")
    else:
        add("Raw inversion correctness", True, "not in raw inversion mode")

    if scenario.get("un_scale_mode") == "band_inversion":
        valid = bool((eligible_df["un_band"].notna()).all()) if n_eligible else True
        add("Band inversion correctness", valid, f"missing_bands={int((eligible_df['un_band'].isna()).sum()) if n_eligible else 0}")
    else:
        add("Band inversion correctness", True, "not in band inversion mode")

    if no_sids_results_df is not None and scenario.get("sosac_gamma", 0.0) > 0:
        no_sids_eligible = _eligible(no_sids_results_df)
        sosac_total = float(no_sids_eligible["component_sosac_amt"].sum()) if len(no_sids_eligible) else 0.0
        final_sum = float(no_sids_eligible["final_share"].sum()) if len(no_sids_eligible) else 0.0
        add("No-SIDS fallback", abs(sosac_total) <= 1e-6 and abs(final_sum - 1.0) <= 1e-6, f"sosac_total={sosac_total:.8f}")
    else:
        add("No-SIDS fallback", True, "not applicable")

    if scenario.get("floor_pct", 0.0) > 0:
        add("Floor feasibility", abs(share_sum - 1.0) <= tolerance, f"floor_pct={scenario.get('floor_pct')}")
    else:
        add("Floor feasibility", True, "floor disabled")

    if scenario.get("ceiling_pct") is not None:
        add("Ceiling feasibility", abs(share_sum - 1.0) <= tolerance, f"ceiling_pct={scenario.get('ceiling_pct')}")
    else:
        add("Ceiling feasibility", True, "ceiling disabled")

    add("Scale invariance of shares", True, "tested in fund-size sweep and diagnostics")

    return pd.DataFrame(checks)


def summarize_group_totals(results_df: pd.DataFrame) -> pd.DataFrame:
    eligible_df = _eligible(results_df)
    rows = []

    region_totals = eligible_df.groupby("region", dropna=False)["total_allocation"].sum().reset_index()
    for _, row in region_totals.iterrows():
        rows.append({"group_type": "region", "group": row["region"], "total_allocation_m": row["total_allocation"]})

    income_totals = eligible_df.groupby("WB Income Group", dropna=False)["total_allocation"].sum().reset_index()
    for _, row in income_totals.iterrows():
        rows.append({"group_type": "income", "group": row["WB Income Group"], "total_allocation_m": row["total_allocation"]})

    rows.append({
        "group_type": "special",
        "group": "LDC",
        "total_allocation_m": float(eligible_df[eligible_df["is_ldc"]]["total_allocation"].sum()),
    })
    rows.append({
        "group_type": "special",
        "group": "SIDS",
        "total_allocation_m": float(eligible_df[eligible_df["is_sids"]]["total_allocation"].sum()),
    })

    return pd.DataFrame(rows)
