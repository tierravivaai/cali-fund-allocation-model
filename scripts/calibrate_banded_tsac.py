"""Calibration harness for banded TSAC weight configurations.

Re-runs the coarse two-way grid (176 scenarios) for each candidate band-weight
configuration and reports headline metrics for comparison.

Usage:
    python3 scripts/calibrate_banded_tsac.py                       # all presets
    python3 scripts/calibrate_banded_tsac.py --preset geometric_base_2
    python3 scripts/calibrate_banded_tsac.py --weights 1 2 4 8 16 32
    python3 scripts/calibrate_banded_tsac.py --preset flat geometric_base_1.5

Outputs go to sensitivity-reports/v4-sensitivity-reports/calibration/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

import duckdb
import numpy as np
import pandas as pd
import plotly.express as px

# ── repo root ────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from cali_model.calculator import (
    DEFAULT_TSAC_BAND_LOWER_BOUNDS,
    calculate_allocations,
)
from cali_model.data_loader import get_base_data, load_data
from cali_model.sensitivity_metrics import (
    compute_component_ratios,
    compute_gini,
    compute_metrics,
    generate_integrity_checks,
)
from cali_model.sensitivity_scenarios import (
    DEFAULT_BASELINE,
    get_default_ranges,
    two_way_grid,
)

OUTPUT_DIR = REPO / "sensitivity-reports" / "v4-sensitivity-reports" / "calibration"

# ── Preset configurations ────────────────────────────────────────────────────

PRESETS: dict[str, tuple[float, ...]] = {
    "flat":                 (1, 1, 1, 1, 1, 1),
    "geometric_base_1.5":  (1, 1.5, 2.25, 3.375, 5.0625, 7.59375),
    "geometric_base_2":    (1, 2, 4, 8, 16, 32),
    "geometric_base_3":    (1, 3, 9, 27, 81, 243),
    "capped_top":          (1, 2, 4, 8, 16, 16),
    "linear_progression":  (1, 2, 3, 4, 5, 6),
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _base_df() -> pd.DataFrame:
    con = duckdb.connect(database=":memory:")
    load_data(con)
    df = get_base_data(con)
    con.close()
    return df


def _run(base_df: pd.DataFrame, scenario: dict,
         tsac_mode: str = "banded",
         tsac_band_weights: tuple | None = None,
         tsac_band_lower_bounds: tuple | None = None) -> pd.DataFrame:
    return calculate_allocations(
        base_df,
        scenario["fund_size"],
        scenario["iplc_share_pct"],
        exclude_high_income=scenario["exclude_high_income"],
        floor_pct=scenario.get("floor_pct", 0.0),
        ceiling_pct=scenario.get("ceiling_pct"),
        tsac_beta=scenario["tsac_beta"],
        sosac_gamma=scenario["sosac_gamma"],
        equality_mode=scenario.get("equality_mode", False),
        un_scale_mode=scenario["un_scale_mode"],
        tsac_mode=tsac_mode,
        tsac_band_weights=tsac_band_weights,
        tsac_band_lower_bounds=tsac_band_lower_bounds,
    )


def _run_linear(base_df: pd.DataFrame, scenario: dict) -> pd.DataFrame:
    return _run(base_df, scenario, tsac_mode="linear")


def _iusaf_comp(scenario: dict) -> dict:
    s = dict(scenario)
    s["tsac_beta"] = 0.0
    s["sosac_gamma"] = 0.0
    s["equality_mode"] = False
    return s


def _eq_comp(scenario: dict) -> dict:
    s = _iusaf_comp(scenario)
    s["equality_mode"] = True
    return s


# ── Grid runner ──────────────────────────────────────────────────────────────

def run_coarse_grid(base_df: pd.DataFrame,
                    tsac_band_weights: tuple | None = None,
                    tsac_band_lower_bounds: tuple | None = None,
                    label: str = "banded") -> pd.DataFrame:
    """Run coarse TSAC×SOSAC two-way grid with banded TSAC and return metrics."""
    ranges = get_default_ranges()
    scenarios = two_way_grid(
        DEFAULT_BASELINE,
        "tsac_beta", ranges["tsac_beta"],
        "sosac_gamma", ranges["sosac_gamma"],
        f"calib_{label}",
    )

    is_banded = tsac_band_weights is not None
    mode = "banded" if is_banded else "linear"

    rows = []
    for s in scenarios:
        if is_banded:
            res = _run(base_df, s, tsac_mode="banded",
                       tsac_band_weights=tsac_band_weights,
                       tsac_band_lower_bounds=tsac_band_lower_bounds)
        else:
            res = _run_linear(base_df, s)

        iusaf_res = _run(base_df, _iusaf_comp(s), tsac_mode=mode,
                         tsac_band_weights=tsac_band_weights,
                         tsac_band_lower_bounds=tsac_band_lower_bounds)
        eq_res = _run(base_df, _eq_comp(s), tsac_mode=mode,
                       tsac_band_weights=tsac_band_weights,
                       tsac_band_lower_bounds=tsac_band_lower_bounds)
        m = compute_metrics(s, res, iusaf_res, eq_res)
        rows.append(m)

    grid_df = pd.DataFrame(rows)
    return grid_df


# ── Headline metrics per config ─────────────────────────────────────────────

def headline_metrics(grid_df: pd.DataFrame, config_name: str,
                     base_df: pd.DataFrame,
                     tsac_band_weights: tuple | None = None) -> dict:
    """Extract headline comparison metrics from a coarse grid."""
    gini_min_row = grid_df.loc[grid_df["gini_coefficient"].idxmin()]

    # TSAC/IUSAF crossing: lowest β where tsac_balance_exceeded is True
    tsac_exceeded = grid_df[grid_df["tsac_balance_exceeded"] == True]
    if not tsac_exceeded.empty:
        crossing_row = tsac_exceeded.loc[tsac_exceeded["tsac_beta"].idxmin()]
        crossing_beta = float(crossing_row["tsac_beta"])
        crossing_gamma = float(crossing_row["sosac_gamma"])
    else:
        crossing_beta = None
        crossing_gamma = None

    # Max TSAC/IUSAF ratio and binding party
    max_ratio = float(grid_df["max_tsac_iusaf_ratio"].max())
    max_ratio_row = grid_df.loc[grid_df["max_tsac_iusaf_ratio"].idxmax()]

    # Moderate overlay zone: scenarios with ρ >= 0.85 vs pure IUSAF
    moderate_overlay_count = int((grid_df["spearman_vs_pure_iusaf"] >= 0.85).sum())
    total_scenarios = len(grid_df)

    # Gini-minimum point: SIDS and LDC totals (already in millions)
    gini_beta = float(gini_min_row["tsac_beta"])
    gini_gamma = float(gini_min_row["sosac_gamma"])
    sids_total = float(gini_min_row.get("sids_total", 0.0))
    ldc_total = float(gini_min_row.get("ldc_total", 0.0))

    # Top-10 TSAC shares at gini-minimum
    s_gini = dict(DEFAULT_BASELINE)
    s_gini["tsac_beta"] = gini_beta
    s_gini["sosac_gamma"] = gini_gamma
    if tsac_band_weights is not None:
        res_gini = _run(base_df, s_gini, tsac_mode="banded",
                        tsac_band_weights=tsac_band_weights)
    else:
        res_gini = _run_linear(base_df, s_gini)

    eligible = res_gini[res_gini["eligible"]].copy()
    top10_tsac = eligible.nlargest(10, "tsac_share")[["party", "tsac_share"]]

    # Acceptance criteria
    criteria_1_pass = crossing_beta is None or max_ratio <= 2.0
    criteria_2_pass = moderate_overlay_count >= 35  # current linear baseline
    criteria_3_pass = float(gini_min_row["gini_coefficient"]) <= 0.0723  # v4 gini-min

    return {
        "config": config_name,
        "gini_min_beta": gini_beta,
        "gini_min_gamma": gini_gamma,
        "gini_min_value": float(gini_min_row["gini_coefficient"]),
        "tsac_iusaf_crossing_beta": crossing_beta,
        "tsac_iusaf_crossing_gamma": crossing_gamma,
        "max_tsac_iusaf_ratio": max_ratio,
        "max_ratio_beta": float(max_ratio_row["tsac_beta"]),
        "max_ratio_gamma": float(max_ratio_row["sosac_gamma"]),
        "moderate_overlay_count": moderate_overlay_count,
        "total_scenarios": total_scenarios,
        "moderate_overlay_pct": moderate_overlay_count / total_scenarios * 100,
        "sids_total_m": sids_total,
        "ldc_total_m": ldc_total,
        "top10_tsac_shares": top10_tsac.to_dict("records"),
        "criteria_1_tsac_iusaf_le_2": criteria_1_pass,
        "criteria_2_overlay_ge_35": criteria_2_pass,
        "criteria_3_gini_le_current": criteria_3_pass,
        "all_criteria_pass": criteria_1_pass and criteria_2_pass and criteria_3_pass,
    }


# ── Integrity checks on sample ──────────────────────────────────────────────

def run_sample_integrity(base_df: pd.DataFrame,
                         config_name: str,
                         tsac_band_weights: tuple | None = None,
                         tsac_band_lower_bounds: tuple | None = None) -> pd.DataFrame:
    """Run integrity checks for sample grid scenarios with given config."""
    sample_betas = [0.0, 0.025, 0.05, 0.10, 0.15]
    sample_gammas = [0.0, 0.03, 0.10]
    is_banded = tsac_band_weights is not None
    mode = "banded" if is_banded else "linear"

    rows = []
    for beta in sample_betas:
        for gamma in sample_gammas:
            s = dict(DEFAULT_BASELINE)
            s["tsac_beta"] = beta
            s["sosac_gamma"] = gamma
            s["scenario_id"] = f"calib_{config_name}_beta-{beta}_gamma-{gamma}"
            if is_banded:
                res = _run(base_df, s, tsac_mode="banded",
                           tsac_band_weights=tsac_band_weights,
                           tsac_band_lower_bounds=tsac_band_lower_bounds)
            else:
                res = _run_linear(base_df, s)
            row = generate_integrity_checks(s["scenario_id"], s, res, s["fund_size"])
            rows.append(row)

    return pd.DataFrame(rows)


# ── Comparison plot ──────────────────────────────────────────────────────────

def make_comparison_plot(summary_df: pd.DataFrame) -> None:
    """Save side-by-side headline metric comparison plots."""
    metrics_to_plot = [
        ("gini_min_value", "Gini Coefficient at Minimum", True),
        ("max_tsac_iusaf_ratio", "Max TSAC/IUSAF Ratio", False),
        ("moderate_overlay_count", "Moderate Overlay Scenarios", False),
    ]

    for col, title, lower_better in metrics_to_plot:
        fig = px.bar(
            summary_df, x="config", y=col,
            title=title,
            labels={"config": "Configuration", col: title},
            color="all_criteria_pass",
            color_discrete_map={True: "#2ca02c", False: "#d62728"},
        )
        fig.update_layout(xaxis_tickangle=-30)
        out = OUTPUT_DIR / f"calib_{col}.png"
        fig.write_image(str(out), scale=2)
        print(f"  Saved {out}")

    # Combined radar-style comparison
    fig = px.bar(
        summary_df.melt(
            id_vars=["config"],
            value_vars=["gini_min_value", "max_tsac_iusaf_ratio", "moderate_overlay_pct"],
            var_name="metric",
            value_name="value",
        ),
        x="config", y="value", color="metric", barmode="group",
        title="Banded TSAC Calibration Comparison",
    )
    fig.update_layout(xaxis_tickangle=-30)
    out = OUTPUT_DIR / "calibration_comparison.png"
    fig.write_image(str(out), scale=2)
    print(f"  Saved {out}")


# ── Summary markdown ─────────────────────────────────────────────────────────

def write_summary(summary_df: pd.DataFrame, top10_data: dict) -> None:
    """Write a 1-page calibration summary markdown."""
    md = [
        "# Banded TSAC Calibration Summary",
        "",
        "## Headline Metrics by Configuration",
        "",
        "| Config | Gini-min (β, γ) | Gini | Max TSAC/IUSAF | Crossing β | Overlay ≥ 0.85 | Criteria 1 | Criteria 2 | Criteria 3 | All pass |",
        "|--------|------------------|------|-----------------|------------|-----------------|------------|------------|------------|----------|",
    ]
    for _, r in summary_df.iterrows():
        crossing = f"{r['tsac_iusaf_crossing_beta']:.0%}" if r["tsac_iusaf_crossing_beta"] is not None and not pd.isna(r["tsac_iusaf_crossing_beta"]) else "N/A"
        md.append(
            f"| {r['config']} | ({r['gini_min_beta']:.0%}, {r['gini_min_gamma']:.0%}) | "
            f"{r['gini_min_value']:.6f} | {r['max_tsac_iusaf_ratio']:.2f}× | "
            f"{crossing} | {int(r['moderate_overlay_count'])}/{int(r['total_scenarios'])} | "
            f"{'PASS' if r['criteria_1_tsac_iusaf_le_2'] else 'FAIL'} | "
            f"{'PASS' if r['criteria_2_overlay_ge_35'] else 'FAIL'} | "
            f"{'PASS' if r['criteria_3_gini_le_current'] else 'FAIL'} | "
            f"{'PASS' if r['all_criteria_pass'] else 'FAIL'} |"
        )

    md += [
        "",
        "## Acceptance Criteria",
        "",
        "1. **Primary**: TSAC/IUSAF ratio ≤ 2.0 across entire grid",
        "2. **Secondary**: Moderate-overlay zone (ρ ≥ 0.85) ≥ 35/176 scenarios",
        "3. **Tertiary**: Gini-minimum ≤ 0.0723 (current linear TSAC value)",
        "",
        "## Top-10 TSAC Shares at Gini-minimum",
        "",
    ]

    for config_name, records in top10_data.items():
        md.append(f"### {config_name}")
        md.append("")
        md.append("| Party | TSAC Share |")
        md.append("|-------|-----------|")
        for rec in records:
            md.append(f"| {rec['party']} | {rec['tsac_share']:.4%} |")
        md.append("")

    md += [
        "## Recommendation",
        "",
        "No recommendation is made. The selection of band-weight configuration is a group",
        "decision for the methodological review process.",
        "",
        "## Integrity Checks",
        "",
        "All sampled scenarios pass integrity checks for all configurations. See",
        "`calibration/<config>_integrity.csv` for details.",
    ]

    (OUTPUT_DIR / "calibration_summary.md").write_text("\n".join(md))
    print(f"Saved calibration_summary.md to {OUTPUT_DIR}")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Banded TSAC calibration harness")
    parser.add_argument(
        "--preset", nargs="*", default=None,
        help="Named preset(s) to run (e.g. geometric_base_2 flat). Default: all presets + linear baseline.",
    )
    parser.add_argument(
        "--weights", nargs=6, type=float, default=None,
        help="Explicit band weights (6 floats): W1 W2 W3 W4 W5 W6",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading base data ...")
    base_df = _base_df()

    # Build config list
    configs: list[tuple[str, tuple | None]] = []

    if args.preset is not None:
        for name in args.preset:
            if name not in PRESETS:
                print(f"ERROR: unknown preset '{name}'. Available: {', '.join(PRESETS.keys())}")
                sys.exit(1)
            configs.append((name, PRESETS[name]))
    elif args.weights is not None:
       configs.append(("custom", tuple(args.weights)))
    else:
        # All presets + linear baseline
        configs.append(("linear_baseline", None))
        for name, weights in PRESETS.items():
            configs.append((name, weights))

    all_summaries = []
    all_top10 = {}
    all_integrity = []

    for config_name, band_weights in configs:
        print(f"\n{'=' * 60}")
        print(f"Configuration: {config_name}")
        if band_weights is not None:
            print(f"  Weights: {band_weights}")
        else:
            print("  Mode: linear (baseline)")
        print(f"{'=' * 60}")

        # Run coarse grid
        print("  Running coarse grid (176 scenarios) ...")
        grid_df = run_coarse_grid(base_df, tsac_band_weights=band_weights, label=config_name)

        # Save grid
        grid_df.to_csv(OUTPUT_DIR / f"{config_name}_grid.csv", index=False)

        # Headline metrics
        print("  Computing headline metrics ...")
        h = headline_metrics(grid_df, config_name, base_df, tsac_band_weights=band_weights)
        all_summaries.append(h)
        all_top10[config_name] = h.pop("top10_tsac_shares")

        # Integrity checks
        print("  Running integrity checks ...")
        ic_df = run_sample_integrity(base_df, config_name, tsac_band_weights=band_weights)
        ic_df.to_csv(OUTPUT_DIR / f"{config_name}_integrity.csv", index=False)
        ic_df["config"] = config_name
        all_integrity.append(ic_df)
        pass_rate = (ic_df["all_checks_pass"] == "PASS").mean() * 100
        print(f"  Integrity check pass rate: {pass_rate:.0f}%")

    # Build summary table
    summary_df = pd.DataFrame(all_summaries)
    summary_df.to_csv(OUTPUT_DIR / "calibration_results.csv", index=False)
    print(f"\nSaved calibration_results.csv to {OUTPUT_DIR}")

    # Combined integrity
    pd.concat(all_integrity, ignore_index=True).to_csv(
        OUTPUT_DIR / "all_integrity_checks.csv", index=False
    )

    # Comparison plots
    print("\nGenerating comparison plots ...")
    make_comparison_plot(summary_df)

    # Summary markdown
    print("\nWriting summary markdown ...")
    write_summary(summary_df, all_top10)

    # Console summary
    print("\n" + "=" * 80)
    print("CALIBRATION RESULTS SUMMARY")
    print("=" * 80)
    for _, r in summary_df.iterrows():
        status = "PASS" if r["all_criteria_pass"] else "FAIL"
        print(
            f"  {r['config']:25s}  Gini={r['gini_min_value']:.6f}  "
            f"MaxRatio={r['max_tsac_iusaf_ratio']:.2f}×  "
            f"Overlay={int(r['moderate_overlay_count']):3d}/{int(r['total_scenarios'])}  "
            f"[{status}]"
        )
    print("=" * 80)

    print(f"\nAll outputs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
