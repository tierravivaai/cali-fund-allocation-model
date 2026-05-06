#!/usr/bin/env python3
"""Stewardship Pool Volume Analysis
===================================

Generates Tables E1 and E2 from the Option D revision draft, restructured
for clarity. Instead of pipe-separated triple values (IUSAF|TSAC|SOSAC) in
each cell, Table E1 now shows two columns per balance point: IUSAF amount
and Stewardship Pool (TSAC+SOSAC) amount. The total always equals the fund
size, so the reader can verify: IUSAF + Pool = Fund.

Tables produced:
  - component-allocation.csv  — IUSAF and Pool by balance point and fund size
  - stewardship-pool.csv     — Pool % and Pool $ by balance point and fund size
  - component-percentages.csv — IUSAF/TSAC/SOSAC percentage breakdown

Scenario parameters (matching the paper):
  - 142 eligible Parties, exclude high income (except SIDS)
  - SOSAC fixed at 3%
  - Band-inversion mode
  - IPLC share 50%

Balance points:
  - Strict:          TSAC = 1.5%, SOSAC = 3%
  - Gini-minimum:    TSAC = 2.5%, SOSAC = 3%
  - Boundary:        TSAC = 3.0%, SOSAC = 3%

Usage:
  python3 stewardship_pool_analysis.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pandas as pd
from pathlib import Path
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations

# ── Configuration ────────────────────────────────────────────────────────────
FUND_SIZES = [50_000_000, 200_000_000, 500_000_000, 1_000_000_000, 5_000_000_000, 10_000_000_000]
FUND_LABELS = ["$50m", "$200m", "$500m", "$1bn", "$5bn", "$10bn"]
IPLC_PCT = 50
SOSAC = 0.03
EXCLUDE_HI = True
HI_MODE = "exclude_except_sids"
UN_SCALE = "band_inversion"

BALANCE_POINTS = [
    ("Strict (1.5/3)", 0.015, 0.03),
    ("Gini-minimum (2.5/3)", 0.025, 0.03),
    ("Band-order boundary (3/3)", 0.03, 0.03),
]

OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_pool_volumes(con) -> pd.DataFrame:
    """Compute stewardship pool volumes for each balance point and fund size.
    
    For each scenario, the total allocation equals the fund size.
    IUSAF = alpha * fund_size, TSAC = beta * fund_size, SOSAC = gamma * fund_size.
    These are deterministic splits, so we don't need to run the calculator
    for each fund size — we just calculate from the percentages.
    """
    rows = []
    for bp_name, beta, gamma in BALANCE_POINTS:
        alpha = 1 - beta - gamma
        for fund, label in zip(FUND_SIZES, FUND_LABELS):
            iusaf_m = alpha * fund / 1_000_000
            tsac_m = beta * fund / 1_000_000
            sosac_m = gamma * fund / 1_000_000
            pool_m = tsac_m + sosac_m
            state_m = iusaf_m * (IPLC_PCT / 100.0)  # state component
            iplc_m = iusaf_m * (IPLC_PCT / 100.0)  # IPLC component
            rows.append({
                "balance_point": bp_name,
                "fund_label": label,
                "fund_size_usd": fund,
                "iusaf_pct": round(alpha * 100, 1),
                "tsac_pct": round(beta * 100, 1),
                "sosac_pct": round(gamma * 100, 1),
                "pool_pct": round((beta + gamma) * 100, 1),
                "iusaf_m": round(iusaf_m, 1),
                "tsac_m": round(tsac_m, 1),
                "sosac_m": round(sosac_m, 1),
                "pool_m": round(pool_m, 1),
                "state_m": round(state_m, 1),
                "iplc_m": round(iplc_m, 1),
            })
    return pd.DataFrame(rows)


def compute_pool_table(rows_df: pd.DataFrame) -> pd.DataFrame:
    """Generate Table E2: Stewardship pool by balance point and fund size."""
    pivot = rows_df.pivot_table(
        index="fund_label",
        columns="balance_point",
        values=["pool_pct", "pool_m"],
        aggfunc="first",
    )
    # Flatten and restructure
    pool_rows = []
    for fund_label in FUND_LABELS:
        fund_data = rows_df[rows_df["fund_label"] == fund_label]
        row = {"fund_size": fund_label}
        for bp_name, beta, gamma in BALANCE_POINTS:
            bp_data = fund_data[fund_data["balance_point"] == bp_name]
            if len(bp_data) > 0:
                row[f"{bp_name}_pool_pct"] = bp_data.iloc[0]["pool_pct"]
                row[f"{bp_name}_pool_m"] = bp_data.iloc[0]["pool_m"]
        pool_rows.append(row)
    return pd.DataFrame(pool_rows)


def compute_component_table(rows_df: pd.DataFrame) -> pd.DataFrame:
    """Generate restructured Table E1: IUSAF and Pool by balance point and fund size.
    
    Two columns per balance point: IUSAF amount and Pool amount.
    Total = IUSAF + Pool = Fund size (verifiable).
    """
    table_rows = []
    for fund_label in FUND_LABELS:
        fund_data = rows_df[rows_df["fund_label"] == fund_label]
        row = {"fund_size": fund_label}
        for bp_name, beta, gamma in BALANCE_POINTS:
            bp_data = fund_data[fund_data["balance_point"] == bp_name]
            if len(bp_data) > 0:
                row[f"{bp_name}_iusaf_m"] = bp_data.iloc[0]["iusaf_m"]
                row[f"{bp_name}_pool_m"] = bp_data.iloc[0]["pool_m"]
        table_rows.append(row)
    return pd.DataFrame(table_rows)


def compute_percentage_table(rows_df: pd.DataFrame) -> pd.DataFrame:
    """Generate component percentage breakdown by balance point."""
    pct_rows = []
    for bp_name, beta, gamma in BALANCE_POINTS:
        alpha = 1 - beta - gamma
        pct_rows.append({
            "balance_point": bp_name,
            "iusaf_pct": round(alpha * 100, 1),
            "tsac_pct": round(beta * 100, 1),
            "sosac_pct": round(gamma * 100, 1),
            "pool_pct": round((beta + gamma) * 100, 1),
        })
    return pd.DataFrame(pct_rows)


def main():
    print("Computing stewardship pool volumes...")
    con = None  # Not needed for percentage-based calculations, but kept for consistency
    
    # All computations are deterministic from the percentage splits
    rows_df = compute_pool_volumes(con)
    
    # ── 1. Full row-level data ──────────────────────────────────────────
    rows_df.to_csv(OUT_DIR / "component-allocation.csv", index=False, float_format="%.1f")
    print(f"  Saved: component-allocation.csv ({len(rows_df)} rows)")
    
    # ── 2. Restructured Table E1 (IUSAF | Pool) ───────────────────────
    component_table = compute_component_table(rows_df)
    component_table.to_csv(OUT_DIR / "table-e1-component-allocation.csv", index=False, float_format="%.1f")
    print(f"  Saved: table-e1-component-allocation.csv")
    
    # ── 3. Table E2 (Pool % and $) ─────────────────────────────────────
    pool_table = compute_pool_table(rows_df)
    pool_table.to_csv(OUT_DIR / "table-e2-stewardship-pool.csv", index=False, float_format="%.1f")
    print(f"  Saved: table-e2-stewardship-pool.csv")
    
    # ── 4. Percentages ───────────────────────────────────────────────────
    pct_table = compute_percentage_table(rows_df)
    pct_table.to_csv(OUT_DIR / "component-percentages.csv", index=False, float_format="%.1f")
    print(f"  Saved: component-percentages.csv")
    
    # ── Print summary ────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("STEWARDSHIP POOL VOLUME ANALYSIS — SUMMARY")
    print("=" * 80)
    
    print("\nComponent percentages by balance point:")
    print(pct_table.to_string(index=False))
    
    print("\nTable E1 (IUSAF + Pool by balance point and fund size, USD millions):")
    print(component_table.to_string(index=False))
    
    print("\nTable E2 (Stewardship Pool by balance point and fund size):")
    print(pool_table.to_string(index=False))
    
    # Verification
    print("\nVerification (IUSAF + Pool = Fund):")
    for fund_label in FUND_LABELS:
        fund_data = rows_df[rows_df["fund_label"] == fund_label]
        for _, bp_row in fund_data.iterrows():
            check = bp_row["iusaf_m"] + bp_row["pool_m"]
            expected = bp_row["fund_size_usd"] / 1_000_000
            assert abs(check - expected) < 0.2, f"Mismatch: {check} != {expected}"
    print("  All checks passed: IUSAF + Pool = Fund size ✓")


if __name__ == "__main__":
    main()
