#!/usr/bin/env python3
"""
Gini Unconstrained Minimum Analysis
====================================

Investigates the unconstrained Gini minimum — the point where the Gini coefficient
is lowest without requiring that IUSAF band order be preserved. This is compared
against the band-preserving "Gini-minimum" balance point (TSAC=2.5%, SOSAC=3%).

Scenario parameters:
  - Fund: USD 1,000,000,000
  - IPLC share: 50%
  - Exclude high income: True (except SIDS)
  - UN scale mode: band_inversion
  - SOSAC: fixed at 3% throughout
  - TSAC: swept from 0% to 20%

Outputs:
  - gini-sweep.csv          Full TSAC sweep with Gini, band metrics, Spearman
  - top-recipients.csv      Top 30 recipients at the unconstrained minimum
  - component-breakdown.csv  Per-band component shares at the minimum
  - component-concentration.csv  IUSAF vs TSAC concentration comparison
  - balance-point-comparison.csv   Side-by-side comparison of three balance points

Usage:
  python gini_unconstrained_analysis.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import duckdb
import numpy as np
import pandas as pd
from pathlib import Path
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations

# ── Configuration ────────────────────────────────────────────────────────────
FUND = 1_000_000_000
IPLC = 50
SOSAC = 0.03
EXCLUDE_HI = True
HI_MODE = "exclude_except_sids"
UN_SCALE = "band_inversion"

OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Helper functions ─────────────────────────────────────────────────────────

def gini_coefficient(values):
    """Compute Gini coefficient from an array of values."""
    v = np.sort(values)
    n = len(v)
    if n == 0 or np.sum(v) == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * np.sum(idx * v) - (n + 1) * np.sum(v)) / (n * np.sum(v)))


def compute_scenario(base_df, beta):
    """Run a single scenario and return key metrics."""
    df = calculate_allocations(
        base_df, FUND, IPLC,
        exclude_high_income=EXCLUDE_HI,
        high_income_mode=HI_MODE,
        tsac_beta=beta, sosac_gamma=SOSAC,
        equality_mode=False, un_scale_mode=UN_SCALE,
    )
    el = df[df["eligible"]].copy()
    alpha = 1 - beta - SOSAC

    # Gini
    g = gini_coefficient(el["total_allocation"].values)

    # Band metrics
    b5 = el[el["un_band"].str.startswith("Band 5")]
    b6 = el[el["un_band"].str.startswith("Band 6")]
    b5_mean = float(b5["total_allocation"].mean()) if len(b5) > 0 else 0.0
    b6_mean = float(b6["total_allocation"].mean()) if len(b6) > 0 else 0.0
    band_preserved = b5_mean > b6_mean if (len(b5) > 0 and len(b6) > 0) else True
    margin = float((b5_mean - b6_mean) / b5_mean * 100) if b5_mean > 0 else 0.0

    # Spearman vs pure IUSAF
    df_pure = calculate_allocations(
        base_df, FUND, IPLC,
        exclude_high_income=EXCLUDE_HI,
        high_income_mode=HI_MODE,
        tsac_beta=0.0, sosac_gamma=0.0,
        equality_mode=False, un_scale_mode=UN_SCALE,
    )
    el_pure = df_pure[df_pure["eligible"]]
    merged = el[["party", "final_share"]].merge(
        el_pure[["party", "final_share"]], on="party", suffixes=("_cur", "_base"))
    r_cur = merged["final_share_cur"].rank(method="average")
    r_base = merged["final_share_base"].rank(method="average")
    spearman = float(r_cur.corr(r_base, method="pearson"))

    # LDC / SIDS totals
    ldc_total = float(el[el["is_ldc"]]["total_allocation"].sum())
    sids_total = float(el[el["is_sids"]]["total_allocation"].sum())
    ldc_count = int(el["is_ldc"].sum())
    sids_count = int(el["is_sids"].sum())

    # Stewardship > IUSAF count
    n_steward_exceeds = int((el["component_tsac_amt"] + el["component_sosac_amt"] > el["component_iusaf_amt"]).sum())

    return {
        "tsac_pct": beta * 100,
        "sosac_pct": SOSAC * 100,
        "iusaf_pct": alpha * 100,
        "gini": g,
        "spearman": spearman,
        "band_preserved": band_preserved,
        "b5_mean": b5_mean,
        "b6_mean": b6_mean,
        "b5_b6_margin_pct": margin,
        "ldc_total_m": ldc_total,
        "ldc_count": ldc_count,
        "sids_total_m": sids_total,
        "sids_count": sids_count,
        "stewardship_exceeds_iusaf": n_steward_exceeds,
        "n_eligible": len(el),
    }


def compute_top_recipients(base_df, beta, n=30):
    """Return top N recipients for a given scenario."""
    df = calculate_allocations(
        base_df, FUND, IPLC,
        exclude_high_income=EXCLUDE_HI,
        high_income_mode=HI_MODE,
        tsac_beta=beta, sosac_gamma=SOSAC,
        equality_mode=False, un_scale_mode=UN_SCALE,
    )
    el = df[df["eligible"]].copy()
    el = el.sort_values("total_allocation", ascending=False).reset_index(drop=True)
    el.index = el.index + 1

    el["iusaf_frac"] = el["component_iusaf_amt"] / el["total_allocation"]
    el["tsac_frac"] = el["component_tsac_amt"] / el["total_allocation"]
    el["sosac_frac"] = el["component_sosac_amt"] / el["total_allocation"]
    el["ldc"] = el["is_ldc"].map({True: "LDC", False: "-"})
    el["sids"] = el["is_sids"].map({True: "SIDS", False: "-"})
    el["band"] = el["un_band"].fillna("-")

    top = el.head(n).copy()
    return top[["party", "total_allocation", "state_component", "iplc_component",
                "component_iusaf_amt", "component_tsac_amt", "component_sosac_amt",
                "iusaf_frac", "tsac_frac", "sosac_frac",
                "WB Income Group", "ldc", "sids", "band"]]


def compute_component_breakdown(base_df, beta):
    """Per-band component shares for a given scenario."""
    df = calculate_allocations(
        base_df, FUND, IPLC,
        exclude_high_income=EXCLUDE_HI,
        high_income_mode=HI_MODE,
        tsac_beta=beta, sosac_gamma=SOSAC,
        equality_mode=False, un_scale_mode=UN_SCALE,
    )
    el = df[df["eligible"]].copy()

    rows = []
    band_order = ["Band 1: <= 0.001%", "Band 2: 0.001% - 0.01%",
                   "Band 3: 0.01% - 0.1%", "Band 4: 0.1% - 1.0%",
                   "Band 5: 1.0% - 10.0%", "Band 6: > 10.0%"]

    for band in band_order:
        b = el[el["un_band"] == band]
        if len(b) == 0:
            continue
        iusaf_pct = float((b["component_iusaf_amt"] / b["total_allocation"]).mean() * 100)
        tsac_pct = float((b["component_tsac_amt"] / b["total_allocation"]).mean() * 100)
        sosac_pct = float((b["component_sosac_amt"] / b["total_allocation"]).mean() * 100)
        n_exceed = int((b["component_tsac_amt"] > b["component_iusaf_amt"]).sum())
        rows.append({
            "band": band,
            "n_parties": len(b),
            "mean_allocation_m": float(b["total_allocation"].mean()),
            "mean_iusaf_pct": iusaf_pct,
            "mean_tsac_pct": tsac_pct,
            "mean_sosac_pct": sosac_pct,
            "tsac_exceeds_iusaf_count": n_exceed,
        })

    # Total row
    rows.append({
        "band": "Total",
        "n_parties": len(el),
        "mean_allocation_m": float(el["total_allocation"].mean()),
        "mean_iusaf_pct": float((el["component_iusaf_amt"] / el["total_allocation"]).mean() * 100),
        "mean_tsac_pct": float((el["component_tsac_amt"] / el["total_allocation"]).mean() * 100),
        "mean_sosac_pct": float((el["component_sosac_amt"] / el["total_allocation"]).mean() * 100),
        "tsac_exceeds_iusaf_count": int((el["component_tsac_amt"] > el["component_iusaf_amt"]).sum()),
    })

    return pd.DataFrame(rows)


def compute_concentration(base_df, beta):
    """Component concentration: top-N share of each component's budget."""
    df = calculate_allocations(
        base_df, FUND, IPLC,
        exclude_high_income=EXCLUDE_HI,
        high_income_mode=HI_MODE,
        tsac_beta=beta, sosac_gamma=SOSAC,
        equality_mode=False, un_scale_mode=UN_SCALE,
    )
    el = df[df["eligible"]].copy()

    rows = []
    for comp, col in [("IUSAF", "component_iusaf_amt"),
                       ("TSAC", "component_tsac_amt"),
                       ("SOSAC", "component_sosac_amt")]:
        total = el[col].sum()
        for n in [1, 5, 10, 20]:
            topn = el.nlargest(n, col)[col].sum()
            rows.append({
                "component": comp,
                "top_n": n,
                "share_pct": float(topn / total * 100),
                "budget_m": float(total),
            })

    return pd.DataFrame(rows)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    con = duckdb.connect(database=":memory:")
    load_data(con)
    base_df = get_base_data(con)

    # ── 1. Full TSAC sweep ────────────────────────────────────────────────
    print("Computing TSAC sweep (0%–20%)...")
    sweep_rows = []
    for beta_pct in [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     5.1, 5.2, 5.3, 5.35, 5.4, 5.5, 6.0, 7.0, 8.0, 9.0,
                     10.0, 12.0, 15.0, 20.0]:
        beta = beta_pct / 100.0
        if beta + SOSAC >= 1.0:
            continue
        row = compute_scenario(base_df, beta)
        sweep_rows.append(row)

    sweep_df = pd.DataFrame(sweep_rows)
    sweep_df.to_csv(OUT_DIR / "gini-sweep.csv", index=False, float_format="%.6g")
    print(f"  Saved: gini-sweep.csv ({len(sweep_df)} rows)")

    # ── 2. Top recipients at unconstrained minimum ────────────────────────
    print("Computing top recipients at TSAC=5.35%...")
    top_df = compute_top_recipients(base_df, 0.0535)
    top_df.to_csv(OUT_DIR / "top-recipients.csv", index=True, float_format="%.4g")
    print(f"  Saved: top-recipients.csv ({len(top_df)} rows)")

    # ── 3. Component breakdown at unconstrained minimum ──────────────────
    print("Computing component breakdown at TSAC=5.35%...")
    comp_df = compute_component_breakdown(base_df, 0.0535)
    comp_df.to_csv(OUT_DIR / "component-breakdown.csv", index=False, float_format="%.4g")
    print(f"  Saved: component-breakdown.csv")

    # ── 4. Component concentration ──────────────────────────────────────────
    print("Computing component concentration at TSAC=5.35%...")
    conc_df = compute_concentration(base_df, 0.0535)
    conc_df.to_csv(OUT_DIR / "component-concentration.csv", index=False, float_format="%.4g")
    print(f"  Saved: component-concentration.csv")

    # ── 5. Balance-point comparison ────────────────────────────────────────
    print("Computing balance-point comparison...")
    bp_rows = []
    scenarios = [
        ("Strict", 0.015, 0.03),
        ("Gini-minimum (band-preserved)", 0.025, 0.03),
        ("Band-order boundary", 0.03, 0.03),
        ("Unconstrained Gini minimum", 0.0535, 0.03),
    ]
    for name, beta, gamma in scenarios:
        row = compute_scenario(base_df, beta)
        row["name"] = name
        bp_rows.append(row)

    bp_df = pd.DataFrame(bp_rows)
    # Reorder columns
    cols = ["name", "tsac_pct", "sosac_pct", "iusaf_pct", "gini", "spearman",
            "band_preserved", "b5_mean", "b6_mean", "b5_b6_margin_pct",
            "ldc_total_m", "ldc_count", "sids_total_m", "sids_count",
            "stewardship_exceeds_iusaf", "n_eligible"]
    bp_df = bp_df[cols]
    bp_df.to_csv(OUT_DIR / "balance-point-comparison.csv", index=False, float_format="%.6g")
    print(f"  Saved: balance-point-comparison.csv")

    # ── 6. Also generate comparison data for band-preserved vs unconstrained ──
    # Component breakdown at band-preserved Gini minimum (2.5%)
    print("Computing component breakdown at TSAC=2.5% (band-preserved)...")
    comp_bp_df = compute_component_breakdown(base_df, 0.025)
    comp_bp_df.to_csv(OUT_DIR / "component-breakdown-band-preserved.csv", index=False, float_format="%.4g")
    print(f"  Saved: component-breakdown-band-preserved.csv")

    # ── Summary ────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("GINI UNCONSTRAINED MINIMUM ANALYSIS — SUMMARY")
    print("=" * 80)

    # Find unconstrained minimum
    gini_min_row = sweep_df.loc[sweep_df["gini"].idxmin()]

    # Band-preserved Gini at 2.5%
    gini_bp = sweep_df[sweep_df["tsac_pct"] == 2.5].iloc[0]

    print(f"\nBand-preserving Gini-minimum (TSAC=2.5%):")
    print(f"  Gini = {gini_bp['gini']:.6f}")
    print(f"  Band order preserved: {gini_bp['band_preserved']} (margin {gini_bp['b5_b6_margin_pct']:.1f}%)")
    print(f"  Spearman ρ = {gini_bp['spearman']:.3f}")

    print(f"\nUnconstrained Gini minimum (TSAC={gini_min_row['tsac_pct']:.2f}%):")
    print(f"  Gini = {gini_min_row['gini']:.6f}")
    print(f"  Band order preserved: {gini_min_row['band_preserved']} (margin {gini_min_row['b5_b6_margin_pct']:.1f}%)")
    print(f"  Spearman ρ = {gini_min_row['spearman']:.3f}")
    print(f"  Gini improvement: {(gini_bp['gini'] - gini_min_row['gini']) / gini_bp['gini'] * 100:.1f}% relative")

    print(f"\nOutputs in: {OUT_DIR}")


if __name__ == "__main__":
    main()
