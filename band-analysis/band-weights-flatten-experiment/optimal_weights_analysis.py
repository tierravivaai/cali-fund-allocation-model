#!/usr/bin/env python3
"""
Optimal Band Weight Analysis
=============================

Finds the weight profile that minimises the Gini coefficient subject to a
policy constraint: Band 1 (the least-developed countries) must receive at
least R times what Band 6 (China) receives.

The intuition is simple: pure equality (Gini = 0) treats every Party the
same regardless of their contribution level. But the IUSAF exists precisely
because Parties with smaller UN assessments should receive more. The B1/B6
ratio captures this "differentiation floor" — how much more should the
poorestcountries receive than the largest contributor?

By sweeping this floor, we trace out the efficient frontier: for each
minimum differentiation ratio R, the optimal weights are the flattest
profile that still satisfies B1/B6 >= R. Flatter weights give lower Gini,
so the optimum is always on the boundary (B1/B6 = R exactly).

Outputs:
  - optimal-sweep.csv         Gini and weight details for each B1/B6 floor
  - optimal-profiles-detail.csv  Per-band allocations at key floor ratios
  - efficient-frontier.csv      B1/B6 ratio vs Gini for the frontier

Usage:
  python3 band-analysis/band-weights-flatten/optimal_weights_analysis.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import duckdb
import numpy as np
import pandas as pd
import yaml
import tempfile
from pathlib import Path
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations, load_band_config

# ── Configuration ────────────────────────────────────────────────────────────
FUND = 1_000_000_000
IPLC = 50
BETA = 0.0
GAMMA = 0.0
EXCLUDE_HI = True
HI_MODE = "exclude_except_sids"
UN_SCALE = "band_inversion"

OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

CURRENT_WEIGHTS = [1.50, 1.30, 1.10, 0.95, 0.75, 0.40]
BAND_LABELS = [
    "Band 1: <= 0.001%", "Band 2: 0.001% - 0.01%", "Band 3: 0.01% - 0.1%",
    "Band 4: 0.1% - 1.0%", "Band 5: 1.0% - 10.0%", "Band 6: > 10.0%"
]
BAND_SHORT = ["Band 1", "Band 2", "Band 3", "Band 4", "Band 5", "Band 6"]

# Band sizes (from the data)
BAND_SIZES = [31, 59, 30, 18, 3, 1]

# ── Helper functions ─────────────────────────────────────────────────────────

def gini_coeff(values):
    v = np.sort(values)
    n = len(v)
    if n == 0 or np.sum(v) == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * np.sum(idx * v) - (n + 1) * np.sum(v)) / (n * np.sum(v)))


def write_band_config(weights, tmpdir):
    """Write a temporary band config YAML with the given weights."""
    thresholds = [
        (-0.0001, 0.001), (0.001, 0.01), (0.01, 0.1),
        (0.1, 1.0), (1.0, 10.0), (10.0, None)
    ]
    bands = []
    for i, (w, (mn, mx)) in enumerate(zip(weights, thresholds)):
        band = {"id": i + 1, "weight": float(w), "label": BAND_LABELS[i]}
        if mn is not None:
            band["min_threshold"] = mn
        if mx is not None:
            band["max_threshold"] = mx
        else:
            band["min_threshold"] = 10.0
        bands.append(band)
    config = {"bands": bands}
    path = os.path.join(tmpdir, "bands.yaml")
    with open(path, "w") as f:
        yaml.dump(config, f)
    return path


def compute_with_weights(base_df, weights, tmpdir):
    """Run the calculator with a custom band config and return the eligible df."""
    config_path = write_band_config(weights, tmpdir)

    import cali_model.calculator as calc_mod
    original_load = calc_mod.load_band_config

    def mock_load():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    calc_mod.load_band_config = mock_load

    try:
        df = calculate_allocations(
            base_df, FUND, IPLC,
            exclude_high_income=EXCLUDE_HI,
            high_income_mode=HI_MODE,
            tsac_beta=BETA, sosac_gamma=GAMMA,
            equality_mode=False, un_scale_mode=UN_SCALE,
        )
    finally:
        calc_mod.load_band_config = original_load

    el = df[df["eligible"]].copy()
    return el


def get_band_means(el, weights):
    """Get per-band mean allocations as a dict."""
    means = {}
    for label in BAND_LABELS:
        bdf = el[el["un_band"] == label]
        means[label] = float(bdf["total_allocation"].mean()) if len(bdf) > 0 else 0.0
    return means


def weights_from_ratio(ratio_target):
    """
    Find the flattest (lowest spread) linear weight profile where B1/B6 = ratio_target.
    
    For linear weights: w_i = w1 - (w1 - w6) * (i-1)/5
    B1/B6 ratio = w1/w6 when all bands have positive weights.
    
    With the additional constraint that w6 >= w6_min (floor for China):
    w1 = ratio_target * w6
    The flattest profile has the smallest w1 possible.
    """
    return None  # Will be computed in the sweep


# ── Core analysis ─────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    con = duckdb.connect(database=":memory:")
    load_data(con)
    base_df = get_base_data(con)
    tmpdir = tempfile.mkdtemp()

    # ── 1. Parametric sweep: for each target B1/B6 floor ratio, find optimal ─
    # The key insight: since within-band allocation is proportional to weight,
    # and we want to minimise Gini while keeping B1/B6 >= R,
    # the optimal weights are the flattest (lowest spread) satisfying the constraint.
    #
    # With linear weights parameterised by spread t:
    #   w_i = current_w_i * (1 - t) + 1.0 * t   (interpolation toward equality)
    # the B1/B6 ratio is w1/w6, and we want the smallest t such that w1/w6 >= R.
    #
    # But we can also explore different weight SHAPES (not just linear interpolation).
    # For now, we use the linear interpolation family as it's the simplest and
    # covers the relevant space.

    print("\nSweeping B1/B6 floor ratios...")
    
    # We sweep t from 0 (current) to just before 1.0 (equality)
    # and compute B1/B6 ratio and Gini at each point
    sweep_results = []
    
    n_fine = 200
    for i in range(n_fine + 1):
        t = i / n_fine
        weights = [CURRENT_WEIGHTS[j] * (1 - t) + 1.0 * t for j in range(6)]
        # Enforce strict monotonicity
        for j in range(5):
            if weights[j] <= weights[j + 1]:
                weights[j + 1] = weights[j] - 0.001
        
        el = compute_with_weights(base_df, weights, tmpdir)
        g = gini_coeff(el["total_allocation"].values)
        
        band_means = get_band_means(el, weights)
        b1_mean = band_means[BAND_LABELS[0]]
        b6_mean = band_means[BAND_LABELS[5]]
        b5_mean = band_means[BAND_LABELS[4]]
        b1_b6_actual = b1_mean / b6_mean if b6_mean > 0 else float("inf")
        b1_b5_actual = b1_mean / b5_mean if b5_mean > 0 else float("inf")
        b1_b4_actual = b1_mean / band_means[BAND_LABELS[3]] if band_means[BAND_LABELS[3]] > 0 else float("inf")
        
        spread = max(weights) - min(weights)
        
        # LDC and SIDS totals
        ldc_total = float(el[el["is_ldc"]]["total_allocation"].sum())
        sids_total = float(el[el["is_sids"]]["total_allocation"].sum())
        
        # Group-level metrics
        b1_total = float(el[el["un_band"] == BAND_LABELS[0]]["total_allocation"].sum())
        
        sweep_results.append({
            "t": t,
            "w1": weights[0], "w2": weights[1], "w3": weights[2],
            "w4": weights[3], "w5": weights[4], "w6": weights[5],
            "spread": spread,
            "b1_b6_ratio": b1_b6_actual,
            "b1_b5_ratio": b1_b5_actual,
            "b1_b4_ratio": b1_b4_actual,
            "gini": g,
            "b1_mean_m": b1_mean,
            "b6_mean_m": b6_mean,
            "ldc_total_m": ldc_total,
            "sids_total_m": sids_total,
            "b1_total_m": b1_total,
        })

    sweep_df = pd.DataFrame(sweep_results)
    sweep_df.to_csv(OUT_DIR / "optimal-sweep.csv", index=False, float_format="%.6g")
    print(f"  Saved: optimal-sweep.csv ({len(sweep_df)} rows)")

    # ── 2. Identify optimal weights for key floor ratios ─────────────────────
    # For each target R, find the smallest t (flattest weights) such that B1/B6 >= R
    # This gives the minimum-Gini profile satisfying the floor constraint.
    
    target_ratios = [1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 3.75, 4.0]
    
    optimal_results = []
    detail_rows = []
    
    for target_r in target_ratios:
        # Find the flattest profile where B1/B6 >= target_r
        # (i.e., the one with lowest Gini, which means smallest t)
        candidates = sweep_df[sweep_df["b1_b6_ratio"] >= target_r]
        if len(candidates) == 0:
            continue
        
        # The optimal is the one with lowest Gini (flattest weights)
        best_idx = candidates["gini"].idxmin()
        best = candidates.loc[best_idx]
        
        weights = [best["w1"], best["w2"], best["w3"],
                   best["w4"], best["w5"], best["w6"]]
        
        el = compute_with_weights(base_df, weights, tmpdir)
        
        # Full per-band detail
        for i, blabel in enumerate(BAND_LABELS):
            bdf = el[el["un_band"] == blabel]
            ldc_in_band = int(bdf["is_ldc"].sum()) if "is_ldc" in bdf.columns else 0
            sids_in_band = int(bdf["is_sids"].sum()) if "is_sids" in bdf.columns else 0
            detail_rows.append({
                "target_ratio": target_r,
                "band": BAND_SHORT[i],
                "weight": weights[i],
                "n": len(bdf),
                "n_ldc": ldc_in_band,
                "n_sids": sids_in_band,
                "mean_alloc_m": float(bdf["total_allocation"].mean()),
                "total_alloc_m": float(bdf["total_allocation"].sum()),
            })
        
        optimal_results.append({
            "target_ratio": target_r,
            "t": best["t"],
            "w1": best["w1"], "w2": best["w2"], "w3": best["w3"],
            "w4": best["w4"], "w5": best["w5"], "w6": best["w6"],
            "spread": best["spread"],
            "b1_b6_ratio_achieved": best["b1_b6_ratio"],
            "b1_b5_ratio": best["b1_b5_ratio"],
            "gini": best["gini"],
            "b1_mean_m": best["b1_mean_m"],
            "b6_mean_m": best["b6_mean_m"],
            "ldc_total_m": best["ldc_total_m"],
            "sids_total_m": best["sids_total_m"],
            "b1_total_m": best["b1_total_m"],
        })

    optimal_df = pd.DataFrame(optimal_results)
    optimal_df.to_csv(OUT_DIR / "optimal-profiles.csv", index=False, float_format="%.6g")
    print(f"  Saved: optimal-profiles.csv ({len(optimal_df)} profiles)")
    
    detail_df = pd.DataFrame(detail_rows)
    detail_df.to_csv(OUT_DIR / "optimal-profiles-detail.csv", index=False, float_format="%.6g")
    print(f"  Saved: optimal-profiles-detail.csv ({len(detail_df)} rows)")

    # ── 3. Additional: weight shape comparison ─────────────────────────────
    # Compare linear interpolation with convex/concave weight shapes
    # at the same B1/B6 ratio, to see if shape matters
    print("\nComparing weight shapes at key B1/B6 ratios...")
    
    target_ratio = 2.0  # Band 1 gets 2x Band 6
    shape_results = []
    
    for shape_name, shape_fn in [
        ("linear", lambda t: t),  # w = current*(1-t) + 1.0*t
        ("front-loaded", lambda t: t),  # will use different parametric
        ("back-loaded", lambda t: t),
    ]:
        pass  # handled below
    
    # Actually, let's compare three shapes:
    # 1. Linear: w_i = current_i * (1-t) + 1.0 * t
    # 2. Front-loaded: compress top bands more (quadratic toward flat from top)
    # 3. Back-loaded: compress bottom bands more (quadratic toward flat from bottom)
    
    for ratio_target in [1.5, 2.0, 2.5, 3.0]:
        for shape, alpha in [("linear", 1.0), ("front_compress", 0.5), ("back_compress", 2.0)]:
            # Find t such that B1/B6 ≈ ratio_target
            best_t = None
            best_gini = 1.0
            best_weights = None
            
            for t_val in np.arange(0.0, 1.001, 0.005):
                t_val = round(t_val, 4)
                # For linear
                if shape == "linear":
                    w = [CURRENT_WEIGHTS[j] * (1 - t_val) + 1.0 * t_val for j in range(6)]
                elif shape == "front_compress":
                    # Compress top bands (1-3) more, keep bottom bands (4-6) closer to current
                    # Top gets flattened faster, bottom stays steeper
                    top_t = t_val ** alpha  # slower for alpha < 1
                    bot_t = t_val
                    w = []
                    for j in range(6):
                        if j < 3:
                            w.append(CURRENT_WEIGHTS[j] * (1 - top_t) + 1.0 * top_t)
                        else:
                            w.append(CURRENT_WEIGHTS[j] * (1 - bot_t) + 1.0 * bot_t)
                elif shape == "back_compress":
                    # Compress bottom bands (4-6) more, keep top bands (1-3) closer to current
                    top_t = t_val
                    bot_t = t_val ** alpha  # slower for alpha > 1
                    w = []
                    for j in range(6):
                        if j < 3:
                            w.append(CURRENT_WEIGHTS[j] * (1 - top_t) + 1.0 * top_t)
                        else:
                            w.append(CURRENT_WEIGHTS[j] * (1 - bot_t) + 1.0 * bot_t)
                else:
                    continue
                
                # Enforce monotonicity
                for j in range(5):
                    if w[j] <= w[j + 1]:
                        w[j + 1] = w[j] - 0.001
                
                b1_w = w[0]
                b6_w = w[5]
                ratio = b1_w / b6_w if b6_w > 0 else float("inf")
                
                # Check if this is close to our target
                if abs(ratio - ratio_target) > 0.15:
                    continue
                
                el = compute_with_weights(base_df, w, tmpdir)
                g = gini_coeff(el["total_allocation"].values)
                
                if g < best_gini:
                    best_gini = g
                    best_t = t_val
                    best_weights = w
            
            if best_weights is not None:
                el = compute_with_weights(base_df, best_weights, tmpdir)
                band_means = get_band_means(el, best_weights)
                b1_mean = band_means[BAND_LABELS[0]]
                b6_mean = band_means[BAND_LABELS[5]]
                
                spread = max(best_weights) - min(best_weights)
                shape_results.append({
                    "target_ratio": ratio_target,
                    "shape": shape,
                    "t": best_t,
                    "w1": best_weights[0], "w6": best_weights[5],
                    "spread": spread,
                    "b1_b6_achieved": b1_mean / b6_mean if b6_mean > 0 else float("inf"),
                    "gini": best_gini,
                    "b1_mean": b1_mean,
                    "b6_mean": b6_mean,
                })

    if shape_results:
        shape_df = pd.DataFrame(shape_results)
        shape_df.to_csv(OUT_DIR / "weight-shape-comparison.csv", index=False, float_format="%.6g")
        print(f"  Saved: weight-shape-comparison.csv ({len(shape_df)} rows)")

    # ── 4. Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 90)
    print("OPTIMAL BAND WEIGHT ANALYSIS — SUMMARY")
    print("=" * 90)
    
    print("\nOptimal weights by B1/B6 floor ratio (minimum Gini at each floor):")
    print(f"{'Floor R':>8} {'Weights':>30} {'Spread':>7} {'Gini':>8} "
          f"{'B1 mean':>8} {'B6 mean':>8} {'LDC total':>10} {'SIDS total':>10}")
    for row in optimal_results:
        wt = f"{row['w1']:.2f}/{row['w3']:.2f}/{row['w6']:.2f}"
        print(f"{row['target_ratio']:>8.2f} {wt:>30} {row['spread']:>7.2f} {row['gini']:>8.4f} "
              f"{row['b1_mean_m']:>8.2f} {row['b6_mean_m']:>8.2f} "
              f"{row['ldc_total_m']:>10.2f} {row['sids_total_m']:>10.2f}")

    # Key insight
    current = [r for r in optimal_results if r["target_ratio"] == 3.75]
    ratio_2 = [r for r in optimal_results if r["target_ratio"] == 2.0]
    ratio_1_5 = [r for r in optimal_results if r["target_ratio"] == 1.5]
    
    print("\n" + "=" * 90)
    print("KEY FINDINGS")
    print("=" * 90)
    
    if current:
        c = current[0]
        print(f"\nCurrent weights (B1/B6 = {c['b1_b6_ratio_achieved']:.2f}x): Gini = {c['gini']:.4f}")
    if ratio_2:
        r = ratio_2[0]
        print(f"B1/B6 = 2.0x floor:       Gini = {r['gini']:.4f}  (weights: {r['w1']:.2f}→{r['w6']:.2f})")
    if ratio_1_5:
        r = ratio_1_5[0]
        print(f"B1/B6 = 1.5x floor:       Gini = {r['gini']:.4f}  (weights: {r['w1']:.2f}→{r['w6']:.2f})")
    
    if current and ratio_2:
        delta = current[0]['gini'] - ratio_2[0]['gini']
        pct = delta / current[0]['gini'] * 100
        print(f"\nGini reduction from 3.75x to 2.0x floor: {delta:.4f} absolute ({pct:.1f}% relative)")
    
    if shape_results:
        print("\nShape comparison at B1/B6 ≈ 2.0x:")
        for s in shape_results:
            if s["target_ratio"] == 2.0:
                print(f"  {s['shape']:>15}: Gini = {s['gini']:.4f}, spread = {s['spread']:.2f}")

    # Clean up
    import shutil
    shutil.rmtree(tmpdir)
    print(f"\nOutputs in: {OUT_DIR}")


if __name__ == "__main__":
    main()
