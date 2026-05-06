#!/usr/bin/env python3
"""
Optimal Band Weight Analysis — Constrained Optimisation
=========================================================

Finds the weight profile that minimises the Gini coefficient subject to a
policy constraint: Band 1 (LDC-heavy floor) must receive at least R times
what Band 6 (China) receives on a per-country basis.

The key analytical insight: since every country within a band receives the
same weight, the per-band mean allocation is proportional to the weight
alone. This means the B1/B6 allocation ratio equals w1/w6 exactly, and
monotonicity requires only w1 > w2 > w3 > w4 > w5 > w6 > 0.

The optimisation problem is therefore:
    minimise  Gini(w1, ..., w6)
    subject to  w1/w6 >= R       (differentiation floor)
                w_i > w_{i+1}    (strict monotonicity)
                w_i > 0          (positive weights)

Since the weights only affect allocations through the per-band weight
(and 142 Parties are distributed across 6 bands with sizes 31/59/30/18/3/1),
the Gini can be computed directly from the weight vector and band sizes
without running the full calculator. This makes the optimisation fast.

Method: grid search over the 5-dimensional weight space (w1 fixed by ratio
and w6, the remaining 4 are free with monotonicity constraints).

Outputs:
  - efficient-frontier.csv    Gini vs B1/B6 floor ratio (the frontier)
  - optimal-weights.csv       Full weight vector at each floor ratio
  - optimal-allocations.csv   Per-band allocation summary at each floor

Usage:
  python3 band-analysis/band-weights-flatten/optimal_weights_constrained.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import duckdb
import numpy as np
import pandas as pd
import tempfile
from pathlib import Path
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations, load_band_config
import yaml

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

CURRENT_WEIGHTS = np.array([1.50, 1.30, 1.10, 0.95, 0.75, 0.40])
BAND_LABELS = [
    "Band 1: <= 0.001%", "Band 2: 0.001% - 0.01%", "Band 3: 0.01% - 0.1%",
    "Band 4: 0.1% - 1.0%", "Band 5: 1.0% - 10.0%", "Band 6: > 10.0%"
]
BAND_SHORT = ["Band 1", "Band 2", "Band 3", "Band 4", "Band 5", "Band 6"]
BAND_SIZES = np.array([31, 59, 30, 18, 3, 1])  # from data


# ── Pure-math Gini from weights ─────────────────────────────────────────────

def gini_from_weights(weights, band_sizes):
    """
    Compute Gini coefficient directly from band weights and sizes.
    
    Each of the n_i parties in band i receives allocation proportional to w_i.
    Total allocation = sum(n_i * w_i), so each party gets w_i / sum(n_j * w_j).
    The Gini can be computed from this vector of per-party allocations.
    """
    # Expand to per-party values
    party_allocs = []
    for w, n in zip(weights, band_sizes):
        party_allocs.extend([w] * n)
    party_allocs = np.array(party_allocs)
    
    # Gini formula
    v = np.sort(party_allocs)
    n = len(v)
    if n == 0 or np.sum(v) == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * np.sum(idx * v) - (n + 1) * np.sum(v)) / (n * np.sum(v)))


def validate_gini_with_calculator(base_df, weights, tmpdir):
    """Cross-validate against the full calculator."""
    # Write band config
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
    path = os.path.join(tmpdir, "bands_check.yaml")
    with open(path, "w") as f:
        yaml.dump(config, f)

    import cali_model.calculator as calc_mod
    original_load = calc_mod.load_band_config
    def mock_load():
        with open(path, "r") as f:
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
    vals = el["total_allocation"].values
    v = np.sort(vals)
    n = len(v)
    gini_calc = float((2 * np.sum(np.arange(1, n+1) * v) - (n+1) * np.sum(v)) / (n * np.sum(v)))

    # Get per-band means
    band_means = {}
    for label in BAND_LABELS:
        bdf = el[el["un_band"] == label]
        band_means[label] = float(bdf["total_allocation"].mean()) if len(bdf) > 0 else 0.0
    
    return gini_calc, band_means, el


def find_optimal_weights(target_ratio, band_sizes, n_grid=40):
    """
    Find the weight vector that minimises Gini subject to w1/w6 >= target_ratio
    and strict monotonicity.
    
    Strategy: since w1/w6 = target_ratio (binding at optimum), and we want
    to minimise spread, we parameterise as:
        w6 = free variable (lower bound)
        w1 = target_ratio * w6
        w2...w5 = interpolated between w1 and w6
    
    For each w6, the interior weights w2...w5 are set to minimise Gini.
    Since Gini depends on the full per-party distribution, interior weights
    that compress more toward the middle (front-loaded flattening) give
    lower Gini because most parties are in Bands 1-3 (90 of 142).
    
    We search over:
    - w6 from 0.3 to 0.95 (Band 6 floor)
    - For each w6, test several interior weight shapes
    
    Returns the weight vector with the lowest Gini.
    """
    best_gini = 1.0
    best_weights = None

    for w6 in np.arange(0.30, 0.96, 0.01):
        w1 = target_ratio * w6
        if w1 <= w6:
            continue  # ratio not achievable
        if w1 > 2.0:
            continue  # cap to avoid extreme weights

        # Generate interior weight shapes
        for shape_param in np.arange(0.2, 3.01, 0.2):
            # Shape parameter controls curvature of interior weights
            # param = 1.0 → linear spacing
            # param < 1.0 → front-compressed (w2 closer to w1, w5 closer to w6)
            # param > 1.0 → back-compressed (w2 closer to w6, w5 closer to w1)

            # Normalised positions (0=w1, 1=w6)
            positions = np.array([1/5, 2/5, 3/5, 4/5])
            # Apply curvature
            curved = positions ** shape_param
            # Map to weight values
            w2 = w1 - curved[0] * (w1 - w6)
            w3 = w1 - curved[1] * (w1 - w6)
            w4 = w1 - curved[2] * (w1 - w6)
            w5 = w1 - curved[3] * (w1 - w6)
            
            weights = [w1, w2, w3, w4, w5, w6]
            
            # Check monotonicity
            monotonic = all(weights[i] > weights[i+1] + 1e-6 for i in range(5))
            if not monotonic:
                continue
            
            g = gini_from_weights(weights, band_sizes)
            if g < best_gini:
                best_gini = g
                best_weights = weights

    return best_weights, best_gini


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading data for validation...")
    con = duckdb.connect(database=":memory:")
    load_data(con)
    base_df = get_base_data(con)
    tmpdir = tempfile.mkdtemp()

    # Validate that pure-math Gini matches calculator
    math_gini = gini_from_weights(list(CURRENT_WEIGHTS), BAND_SIZES)
    calc_gini, _, _ = validate_gini_with_calculator(base_df, list(CURRENT_WEIGHTS), tmpdir)
    print(f"  Math Gini: {math_gini:.6f}, Calculator Gini: {calc_gini:.6f}  (match: {abs(math_gini - calc_gini) < 0.0001})")

    # ── 1. Compute efficient frontier ───────────────────────────────────────
    print("\nComputing efficient frontier (Gini-min at each B1/B6 floor)...")
    
    # Target ratios to evaluate
    target_ratios = np.arange(1.0, 4.01, 0.125)
    
    frontier_rows = []
    optimal_weights_rows = []
    allocation_rows = []
    
    for tr in target_ratios:
        tr_round = round(tr, 3)
        weights, gini = find_optimal_weights(tr_round, BAND_SIZES, n_grid=40)
        
        if weights is None:
            continue
        
        spread = max(weights) - min(weights)
        
        # Compute per-band allocations (mean = weight * fund_per_weight_unit)
        total_weighted = sum(n * w for n, w in zip(BAND_SIZES, weights))
        fund_per_weight = FUND / total_weighted  # in raw units
        # Allocation per party in band i = w_i * fund_per_weight
        # Mean allocation in millions = w_i * fund_per_weight / 1e6
        # But total_allocation in the calculator output is in millions
        
        band_means = [w * fund_per_weight / 1e6 for w in weights]
        band_totals = [n * m for n, m in zip(BAND_SIZES, band_means)]
        
        # LDC/SIDS composition for totals
        # From data: Band 1 has 13 LDC, 22 SIDS; Band 2 has 31 LDC, 11 SIDS; 
        # Band 3 has 0 LDC, 4 SIDS; Band 4 has 0 LDC, 2 SIDS; B5/B6 have 0
        ldc_in_band = np.array([13, 31, 0, 0, 0, 0])
        sids_in_band = np.array([22, 11, 4, 2, 0, 0])
        
        ldc_total = sum(ldc_in_band[i] * band_means[i] for i in range(6))
        sids_total = sum(sids_in_band[i] * band_means[i] for i in range(6))
        
        frontier_rows.append({
            "b1_b6_floor": tr_round,
            "gini": gini,
            "spread": spread,
            "w1": weights[0], "w2": weights[1], "w3": weights[2],
            "w4": weights[3], "w5": weights[4], "w6": weights[5],
            "b1_mean_m": band_means[0],
            "b6_mean_m": band_means[5],
            "ldc_total_m": ldc_total,
            "sids_total_m": sids_total,
        })
        
        optimal_weights_rows.append({
            "b1_b6_floor": tr_round,
            "w1": weights[0], "w2": weights[1], "w3": weights[2],
            "w4": weights[3], "w5": weights[4], "w6": weights[5],
            "gini": gini,
            "spread": spread,
            "b1_b6_ratio": weights[0] / weights[5],
        })
        
        for i in range(6):
            allocation_rows.append({
                "b1_b6_floor": tr_round,
                "band": BAND_SHORT[i],
                "weight": weights[i],
                "n": int(BAND_SIZES[i]),
                "n_ldc": int(ldc_in_band[i]),
                "n_sids": int(sids_in_band[i]),
                "mean_alloc_m": band_means[i],
                "total_alloc_m": band_totals[i],
            })

    frontier_df = pd.DataFrame(frontier_rows)
    frontier_df.to_csv(OUT_DIR / "efficient-frontier.csv", index=False, float_format="%.6g")
    print(f"  Saved: efficient-frontier.csv ({len(frontier_df)} rows)")
    
    weights_df = pd.DataFrame(optimal_weights_rows)
    weights_df.to_csv(OUT_DIR / "optimal-weights.csv", index=False, float_format="%.6g")
    print(f"  Saved: optimal-weights.csv ({len(weights_df)} rows)")
    
    alloc_df = pd.DataFrame(allocation_rows)
    alloc_df.to_csv(OUT_DIR / "optimal-allocations.csv", index=False, float_format="%.6g")
    print(f"  Saved: optimal-allocations.csv ({len(alloc_df)} rows)")

    # ── 2. Validate key points against the calculator ───────────────────────
    print("\nValidating key points against the full calculator...")
    key_floors = [1.5, 2.0, 2.5, 3.0, 3.75]
    for kf in key_floors:
        row = frontier_df[frontier_df["b1_b6_floor"] == kf]
        if len(row) == 0:
            continue
        r = row.iloc[0]
        weights = [r["w1"], r["w2"], r["w3"], r["w4"], r["w5"], r["w6"]]
        calc_gini, band_means_calc, el = validate_gini_with_calculator(
            base_df, weights, tmpdir)
        b1_mean_calc = band_means_calc[BAND_LABELS[0]]
        b6_mean_calc = band_means_calc[BAND_LABELS[5]]
        # LDC/SIDS totals from calculator
        ldc_calc = float(el[el["is_ldc"]]["total_allocation"].sum())
        sids_calc = float(el[el["is_sids"]]["total_allocation"].sum())
        
        print(f"  Floor {kf:.2f}: math_gini={r['gini']:.6f}, calc_gini={calc_gini:.6f}, "
              f"B1/B6={b1_mean_calc/b6_mean_calc:.4f}, "
              f"LDC={ldc_calc:.1f}M, SIDS={sids_calc:.1f}M")

    # ── 3. Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 100)
    print("OPTIMAL BAND WEIGHT ANALYSIS — CONSTRAINT: Minimise Gini s.t. B1/B6 >= R")
    print("=" * 100)
    
    print(f"\n{'Floor':>6} {'Gini':>8} {'w1':>6} {'w2':>6} {'w3':>6} {'w4':>6} {'w5':>6} {'w6':>6} {'Spread':>7} {'B1$M':>7} {'B5$M':>7} {'B6$M':>7} {'LDC$M':>8} {'SIDS$M':>8}")
    for _, r in frontier_df.iterrows():
        if r["b1_b6_floor"] in [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0, 3.5, 3.75]:
            b5m = r["b1_mean_m"] * r["w5"] / r["w1"] if r["w1"] > 0 else 0
            print(f"{r['b1_b6_floor']:>6.2f} {r['gini']:>8.4f} {r['w1']:>6.2f} {r['w2']:>6.2f} "
                  f"{r['w3']:>6.2f} {r['w4']:>6.2f} {r['w5']:>6.2f} {r['w6']:>6.2f} "
                  f"{r['spread']:>7.2f} {r['b1_mean_m']:>7.2f} {b5m:>7.2f} {r['b6_mean_m']:>7.2f} "
                  f"{r['ldc_total_m']:>8.1f} {r['sids_total_m']:>8.1f}")

    print("\n" + "=" * 100)
    print("KEY FINDINGS")
    print("=" * 100)
    
    current_row = frontier_df[frontier_df["b1_b6_floor"] == 3.75]
    r2_row = frontier_df[frontier_df["b1_b6_floor"] == 2.0]
    r15_row = frontier_df[frontier_df["b1_b6_floor"] == 1.5]
    
    if len(current_row) > 0 and len(r2_row) > 0:
        c = current_row.iloc[0]
        r2 = r2_row.iloc[0]
        delta = c["gini"] - r2["gini"]
        print(f"\nCurrent (3.75x): Gini = {c['gini']:.4f}")
        print(f"Optimal at 2.0x: Gini = {r2['gini']:.4f}  → reduction = {delta:.4f}")
        print(f"  Weights: {r2['w1']:.2f} → {r2['w6']:.2f} (spread {r2['spread']:.2f})")
        print(f"  B1 mean: {r2['b1_mean_m']:.2f}M, B6 mean: {r2['b6_mean_m']:.2f}M")
        print(f"  LDC total: {r2['ldc_total_m']:.1f}M, SIDS total: {r2['sids_total_m']:.1f}M")
    
    if len(r15_row) > 0 and len(current_row) > 0:
        r15 = r15_row.iloc[0]
        delta15 = c["gini"] - r15["gini"]
        print(f"\nOptimal at 1.5x: Gini = {r15['gini']:.4f}  → reduction = {delta15:.4f}")
        print(f"  Weights: {r15['w1']:.2f} → {r15['w6']:.2f} (spread {r15['spread']:.2f})")
        print(f"  B1 mean: {r15['b1_mean_m']:.2f}M, B6 mean: {r15['b6_mean_m']:.2f}M")
        print(f"  LDC total: {r15['ldc_total_m']:.1f}M, SIDS total: {r15['sids_total_m']:.1f}M")

    print("\nInterpretation:")
    print("  The B1/B6 ratio is a policy choice representing 'how much more should")
    print("  the poorest countries receive than the largest contributor?'")
    print("  - 1.0x = full equality (Gini = 0)")
    print("  - 1.5x = moderate differentiation (LDC floor countries get 50% more)")
    print("  - 2.0x = standard differentiation (LDCs get double)")
    print("  - 3.75x = current IUSAF (LDCs get 3.75× more than China)")
    print("  Lower ratios give fairer outcomes for middle-income countries")
    print("  while still preserving the principle that the poorest receive more.")

    # Clean up
    import shutil
    shutil.rmtree(tmpdir)
    print(f"\nOutputs in: {OUT_DIR}")


if __name__ == "__main__":
    main()
