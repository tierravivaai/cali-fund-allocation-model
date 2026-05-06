#!/usr/bin/env python3
"""
Band Weight Flattening Analysis
================================

Investigates what happens to allocations between bands under pure IUSAF
(beta=0, gamma=0) as we flatten the band weights from the current steep
profile (1.50 → 0.40) toward equality (all weights = 1.0).

The key question: what flexibility exists to flatten the weights while
preserving monotonic band order (Band 1 mean > Band 2 mean > ... > Band 6 mean)?

Since all countries within a band receive the same weight, the per-band
mean allocation is proportional to the weight itself. So monotonicity
requires only: w1 > w2 > w3 > w4 > w5 > w6 > 0.

The "spread" (max weight − min weight) controls how much redistribution
occurs versus equality. Current spread = 1.10 (1.50 − 0.40). At spread = 0
(all weights = 1.0), every party receives equal share.

Outputs:
  - weight-profiles.csv       All tested weight profiles with Gini and band metrics
  - allocation-by-band.csv     Per-band mean allocation for each profile
  - gini-vs-spread.csv         Gini as a function of weight spread (fine-grained)
  - extreme-profiles.csv      Detailed stats at key weight profiles

Usage:
  python3 band_weights_flatten_analysis.py
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
from cali_model.calculator import calculate_allocations, assign_un_band, load_band_config

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

# Current weights as reference
CURRENT_WEIGHTS = [1.50, 1.30, 1.10, 0.95, 0.75, 0.40]
BAND_LABELS = [
    "Band 1: <= 0.001%", "Band 2: 0.001% - 0.01%", "Band 3: 0.01% - 0.1%",
    "Band 4: 0.1% - 1.0%", "Band 5: 1.0% - 10.0%", "Band 6: > 10.0%"
]
BAND_SHORT = ["Band 1", "Band 2", "Band 3", "Band 4", "Band 5", "Band 6"]

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
    """Run the calculator with a custom band config and return metrics."""
    config_path = write_band_config(weights, tmpdir)

    # Monkey-patch the band config loader
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
    return df, el


def extract_metrics(el, weights, profile_name):
    """Extract key metrics from an eligible DataFrame."""
    g = gini_coeff(el["total_allocation"].values)
    spread = max(weights) - min(weights)
    ratio_1_6 = weights[0] / weights[-1] if weights[-1] > 0 else float("inf")

    band_means = {}
    band_counts = {}
    for i, label in enumerate(BAND_LABELS):
        bdf = el[el["un_band"] == label]
        band_means[f"{BAND_SHORT[i]}_mean"] = float(bdf["total_allocation"].mean()) if len(bdf) > 0 else 0.0
        band_counts[f"{BAND_SHORT[i]}_n"] = len(bdf)

    # Monotonicity check
    means_list = [band_means[f"{b}_mean"] for b in BAND_SHORT]
    monotonic = all(means_list[i] > means_list[i + 1] for i in range(len(means_list) - 1))

    return {
        "profile": profile_name,
        "w1": weights[0], "w2": weights[1], "w3": weights[2],
        "w4": weights[3], "w5": weights[4], "w6": weights[5],
        "spread": spread,
        "b1_b6_ratio": ratio_1_6,
        "gini": g,
        "n_eligible": len(el),
        "monotonic": monotonic,
        **band_means,
        **band_counts,
    }


# ── Weight profiles ──────────────────────────────────────────────────────────

def generate_profiles():
    """Generate a range of weight profiles from steep to flat."""
    profiles = []

    # Named profiles
    named = {
        "Current (1.50→0.40)": [1.50, 1.30, 1.10, 0.95, 0.75, 0.40],
        "Moderate (1.25→0.75)": [1.25, 1.15, 1.05, 0.95, 0.85, 0.75],
        "Flat-linear (1.20→0.80)": [1.20, 1.12, 1.04, 0.96, 0.88, 0.80],
        "Near-flat (1.10→0.90)": [1.10, 1.06, 1.02, 0.98, 0.94, 0.90],
        "Minimal (1.05→0.95)": [1.05, 1.03, 1.01, 0.99, 0.97, 0.95],
        "Equality (1.00→1.00)": [1.00, 1.00, 1.00, 1.00, 1.00, 1.00],
    }
    for name, weights in named.items():
        profiles.append((name, weights))

    # Parametric sweep: linear interpolation between current and equality
    # t=0 is current, t=1 is equality
    for t in np.arange(0.05, 1.0, 0.05):
        t = round(t, 3)
        w = [CURRENT_WEIGHTS[i] * (1 - t) + 1.0 * t for i in range(6)]
        # Ensure strict monotonicity (min gap between adjacent bands)
        min_gap = 0.001
        for i in range(5):
            if w[i] - w[i + 1] < min_gap:
                w[i + 1] = w[i] - min_gap
        name = f"t={t:.2f}"
        profiles.append((name, w))

    return profiles


def generate_fine_spread_sweep():
    """Generate a fine sweep of weight profiles by spread, from current to flat.
    
    Uses linear interpolation between current weights and a 1.0 baseline,
    parameterised by the resulting spread.
    """
    profiles = []
    n_steps = 50
    for i in range(n_steps + 1):
        t = i / n_steps
        w = [CURRENT_WEIGHTS[j] * (1 - t) + 1.0 * t for j in range(6)]
        # Enforce strict monotonicity
        for j in range(5):
            if w[j] <= w[j + 1]:
                w[j + 1] = w[j] - 0.001
        spread = max(w) - min(w)
        profiles.append((f"spread={spread:.3f}", w, spread))
    return profiles


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    con = duckdb.connect(database=":memory:")
    load_data(con)
    base_df = get_base_data(con)

    tmpdir = tempfile.mkdtemp()

    # ── 1. Named and parametric profiles ────────────────────────────────────
    print("Computing weight profiles...")
    all_profiles = generate_profiles()
    profile_rows = []
    allocation_rows = []

    for name, weights in all_profiles:
        df, el = compute_with_weights(base_df, weights, tmpdir)
        metrics = extract_metrics(el, weights, name)
        profile_rows.append(metrics)

        # Per-band allocation detail
        for i, blabel in enumerate(BAND_LABELS):
            bdf = el[el["un_band"] == blabel]
            if len(bdf) > 0:
                allocation_rows.append({
                    "profile": name,
                    "band": BAND_SHORT[i],
                    "weight": weights[i],
                    "n": len(bdf),
                    "mean_alloc_m": float(bdf["total_allocation"].mean()),
                    "total_alloc_m": float(bdf["total_allocation"].sum()),
                })

    profiles_df = pd.DataFrame(profile_rows)
    profiles_df.to_csv(OUT_DIR / "weight-profiles.csv", index=False, float_format="%.6g")
    print(f"  Saved: weight-profiles.csv ({len(profiles_df)} profiles)")

    alloc_df = pd.DataFrame(allocation_rows)
    alloc_df.to_csv(OUT_DIR / "allocation-by-band.csv", index=False, float_format="%.6g")
    print(f"  Saved: allocation-by-band.csv ({len(alloc_df)} rows)")

    # ── 2. Fine-grained spread sweep ──────────────────────────────────────
    print("Computing Gini vs spread sweep...")
    fine_profiles = generate_fine_spread_sweep()
    sweep_rows = []

    for name, weights, spread in fine_profiles:
        df, el = compute_with_weights(base_df, weights, tmpdir)
        g = gini_coeff(el["total_allocation"].values)
        b1m = float(el[el["un_band"].str.startswith("Band 1")]["total_allocation"].mean())
        b6m = float(el[el["un_band"].str.startswith("Band 6")]["total_allocation"].mean())
        b5m = float(el[el["un_band"].str.startswith("Band 5")]["total_allocation"].mean())
        means = [b1m,
                 float(el[el["un_band"].str.startswith("Band 2")]["total_allocation"].mean()),
                 float(el[el["un_band"].str.startswith("Band 3")]["total_allocation"].mean()),
                 float(el[el["un_band"].str.startswith("Band 4")]["total_allocation"].mean()),
                 b5m, b6m]
        monotonic = all(means[i] > means[i + 1] for i in range(5))
        sweep_rows.append({
            "spread": spread,
            "w1": weights[0], "w6": weights[5],
            "b1_b6_ratio": weights[0] / weights[5] if weights[5] > 0 else float("inf"),
            "gini": g,
            "b1_mean": b1m, "b6_mean": b6m, "b5_mean": b5m,
            "b1_b6_mean_ratio": b1m / b6m if b6m > 0 else float("inf"),
            "monotonic": monotonic,
        })

    sweep_df = pd.DataFrame(sweep_rows)
    sweep_df.to_csv(OUT_DIR / "gini-vs-spread.csv", index=False, float_format="%.6g")
    print(f"  Saved: gini-vs-spread.csv ({len(sweep_df)} rows)")

    # ── 3. Extreme profiles detail ──────────────────────────────────────────
    print("Computing extreme profile details...")
    extreme_names = ["Current (1.50→0.40)", "Flat-linear (1.20→0.80)",
                     "Near-flat (1.10→0.90)", "Minimal (1.05→0.95)", "Equality (1.00→1.00)"]
    extreme_rows = []
    for row in profile_rows:
        if row["profile"] in extreme_names:
            extreme_rows.append(row)
    extreme_df = pd.DataFrame(extreme_rows)
    extreme_df.to_csv(OUT_DIR / "extreme-profiles.csv", index=False, float_format="%.6g")
    print(f"  Saved: extreme-profiles.csv ({len(extreme_df)} profiles)")

    # ── Summary ────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("BAND WEIGHT FLATTENING ANALYSIS — SUMMARY")
    print("=" * 80)

    print("\nNamed profiles:")
    for row in profile_rows:
        if not row["profile"].startswith("t="):
            name = row["profile"]
            g = row["gini"]
            spread = row["spread"]
            mono = "Yes" if row["monotonic"] else "No"
            b1m = row["Band 1_mean"]
            b6m = row["Band 6_mean"]
            print(f"  {name:<30} spread={spread:.2f}  Gini={g:.4f}  B1/B6={b1m/b6m:.2f}x  monotonic={mono}")

    # Clean up
    import shutil
    shutil.rmtree(tmpdir)

    print(f"\nOutputs in: {OUT_DIR}")


if __name__ == "__main__":
    main()
