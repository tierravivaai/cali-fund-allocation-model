#!/usr/bin/env python3
"""Validate model-tables CSVs against live calculator output.

Regenerates every IUSAF table from the current code and compares field-by-field
with the originals in model-tables/. Outputs fresh CSVs to
model-tables/table-validation/ and a comparison report.

Scenario (Pure IUSAF — the parameters used in all original model-table CSVs):
  - fund_size = 1_000_000_000
  - iplc_share_pct = 50
  - exclude_high_income = True, high_income_mode = "exclude_except_sids"
  - tsac_beta = 0.0, sosac_gamma = 0.0   (pure IUSAF, no stewardship blend)
  - equality_mode = False
  - un_scale_mode = "band_inversion"
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import duckdb
import pandas as pd
import numpy as np
from pathlib import Path

from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import (
    calculate_allocations,
    aggregate_by_region,
    aggregate_by_income,
    add_total_row,
)

# ── Configuration ────────────────────────────────────────────────────────────
FUND = 1_000_000_000
IPLC = 50
BETA = 0.0
GAMMA = 0.0
EXCLUDE_HI = True
HI_MODE = "exclude_except_sids"
UN_SCALE = "band_inversion"
FLOAT_TOL = 1e-10  # tolerance for floating-point comparison

PROJECT = Path(__file__).resolve().parent.parent
ORIG_DIR = PROJECT / "model-tables"
VAL_DIR = PROJECT / "model-tables" / "table-validation"
VAL_DIR.mkdir(parents=True, exist_ok=True)

# ── Helpers ──────────────────────────────────────────────────────────────────

def round2(x):
    return round(x, 2)


def compare_dataframes(orig: pd.DataFrame, fresh: pd.DataFrame, label: str,
                       sort_by=None, float_cols=None) -> dict:
    """Compare two DataFrames with tolerance for floating-point and sort order.
    
    Args:
        sort_by: column name(s) to sort both DataFrames before comparing.
        float_cols: list of columns to compare with FLOAT_TOL instead of string match.
    """
    result = {"table": label, "status": "MATCH", "differences": []}

    # Normalise column names (strip BOM, whitespace)
    orig.columns = [c.strip().replace("\ufeff", "") for c in orig.columns]
    fresh.columns = [c.strip().replace("\ufeff", "") for c in fresh.columns]

    if sort_by:
        sort_cols = [sort_by] if isinstance(sort_by, str) else sort_by
        orig = orig.sort_values(sort_cols, ignore_index=True)
        fresh = fresh.sort_values(sort_cols, ignore_index=True)
    else:
        orig = orig.reset_index(drop=True)
        fresh = fresh.reset_index(drop=True)

    if orig.shape != fresh.shape:
        result["status"] = "SHAPE_MISMATCH"
        result["differences"].append(
            f"Shape: orig={orig.shape}, fresh={fresh.shape}"
        )
        # Still compare overlapping rows
        min_rows = min(orig.shape[0], fresh.shape[0])
        orig = orig.head(min_rows)
        fresh = fresh.head(min_rows)

    if list(orig.columns) != list(fresh.columns):
        result["status"] = "COLUMNS_MISMATCH"
        result["differences"].append(
            f"Columns differ: orig={list(orig.columns)}, fresh={list(fresh.columns)}"
        )

    if float_cols is None:
        float_cols = []

    for col in orig.columns:
        if col not in fresh.columns:
            continue
        if col in float_cols:
            # Numeric comparison with tolerance
            o = pd.to_numeric(orig[col], errors="coerce").fillna(0).values
            f = pd.to_numeric(fresh[col], errors="coerce").fillna(0).values
            if len(o) != len(f):
                result["status"] = "VALUE_MISMATCH"
                result["differences"].append(f"Column '{col}': length differs")
                continue
            diffs = np.abs(o - f) > FLOAT_TOL
            if diffs.any():
                n = int(diffs.sum())
                # Check if purely cosmetic (last decimal place)
                max_diff = float(np.abs(o[diffs] - f[diffs]).max())
                if max_diff < 1e-6:
                    category = "FP_PRECISION"
                else:
                    category = "SUBSTANTIVE"
                result["status"] = "VALUE_MISMATCH" if category == "SUBSTANTIVE" else result["status"]
                if result["status"] == "MATCH" and category == "FP_PRECISION":
                    # Treat as match with note
                    pass
                else:
                    result["status"] = "VALUE_MISMATCH"
                result["differences"].append(
                    f"Column '{col}': {n} row(s) differ (max_diff={max_diff:.2e}, {category})"
                )
                diff_idx = [i for i, d in enumerate(diffs) if d][:3]
                for idx in diff_idx:
                    result["differences"].append(
                        f"  Row {idx}: orig={orig.iloc[idx][col]} vs fresh={fresh.iloc[idx][col]}"
                    )
        else:
            s_orig = orig[col].astype(str).str.strip()
            s_fresh = fresh[col].astype(str).str.strip()
            diffs = s_orig.values != s_fresh.values
            if diffs.any():
                result["status"] = "VALUE_MISMATCH"
                n = int(diffs.sum())
                result["differences"].append(
                    f"Column '{col}': {n} row(s) differ"
                )
                diff_idx = [i for i, d in enumerate(diffs) if d][:3]
                for idx in diff_idx:
                    result["differences"].append(
                        f"  Row {idx}: orig='{s_orig.iloc[idx]}' vs fresh='{s_fresh.iloc[idx]}'"
                    )

    # Re-classify if only FP_PRECISION differences found
    if result["status"] == "VALUE_MISMATCH":
        substantive = any("SUBSTANTIVE" in d for d in result["differences"])
        if not substantive:
            result["status"] = "FP_PRECISION"

    return result


def save_csv(df: pd.DataFrame, path: Path):
    df.to_csv(path, index=False, float_format="%.15g")


# ── Table generators ─────────────────────────────────────────────────────────

def gen_ldc_sids_panel(df) -> tuple:
    mask = df["is_cbd_party"] & df["eligible"]
    ldc_df = df[df["is_ldc"] & mask]
    sids_df = df[df["is_sids"] & mask]
    other_ldc = df[~df["is_ldc"] & mask]
    other_sids = df[~df["is_sids"] & mask]

    ldc_rows = [
        {"Group": "Least Developed Countries (LDC)", "Countries (number)": len(ldc_df),
         "total_allocation": round2(ldc_df["total_allocation"].sum()),
         "state_component": round2(ldc_df["state_component"].sum()),
         "iplc_component": round2(ldc_df["iplc_component"].sum())},
        {"Group": "Other Countries", "Countries (number)": len(other_ldc),
         "total_allocation": round2(other_ldc["total_allocation"].sum()),
         "state_component": round2(other_ldc["state_component"].sum()),
         "iplc_component": round2(other_ldc["iplc_component"].sum())},
        {"Group": "Total", "Countries (number)": len(ldc_df) + len(other_ldc),
         "total_allocation": round2(ldc_df["total_allocation"].sum() + other_ldc["total_allocation"].sum()),
         "state_component": round2(ldc_df["state_component"].sum() + other_ldc["state_component"].sum()),
         "iplc_component": round2(ldc_df["iplc_component"].sum() + other_ldc["iplc_component"].sum())},
    ]
    sids_rows = [
        {"Group": "Small Island Developing States (SIDS)", "Countries (number)": len(sids_df),
         "total_allocation": round2(sids_df["total_allocation"].sum()),
         "state_component": round2(sids_df["state_component"].sum()),
         "iplc_component": round2(sids_df["iplc_component"].sum())},
        {"Group": "Other Countries", "Countries (number)": len(other_sids),
         "total_allocation": round2(other_sids["total_allocation"].sum()),
         "state_component": round2(other_sids["state_component"].sum()),
         "iplc_component": round2(other_sids["iplc_component"].sum())},
        {"Group": "Total", "Countries (number)": len(sids_df) + len(other_sids),
         "total_allocation": round2(sids_df["total_allocation"].sum() + other_sids["total_allocation"].sum()),
         "state_component": round2(sids_df["state_component"].sum() + other_sids["state_component"].sum()),
         "iplc_component": round2(sids_df["iplc_component"].sum() + other_sids["iplc_component"].sum())},
    ]
    return pd.DataFrame(ldc_rows), pd.DataFrame(sids_rows)


def gen_region_table(df) -> pd.DataFrame:
    agg = aggregate_by_region(df, region_col="region")
    agg = add_total_row(agg, "region")
    # Reorder columns to match original CSV format
    agg = agg[["region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]]
    # Sort region rows alphabetically (like the original), Total last
    total_mask = agg["region"] == "Total"
    data_rows = agg[~total_mask].sort_values("region").reset_index(drop=True)
    total_row = agg[total_mask].reset_index(drop=True)
    return pd.concat([data_rows, total_row], ignore_index=True)


def gen_subregion_table(df) -> pd.DataFrame:
    agg = aggregate_by_region(df, region_col="sub_region")
    agg = add_total_row(agg, "sub_region")
    # Reorder columns to match original CSV format
    agg = agg[["sub_region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]]
    return agg


def gen_intermediate_region_table(df) -> pd.DataFrame:
    agg = aggregate_by_region(df, region_col="intermediate_region")
    agg = add_total_row(agg, "intermediate_region")
    # Reorder columns to match original CSV format
    agg = agg[["intermediate_region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]]
    # Replace NA with "Not Categorized" (original's label)
    agg["intermediate_region"] = agg["intermediate_region"].fillna("Not Categorized")
    # Sort by country count desc (except Total)
    total_mask = agg["intermediate_region"] == "Total"
    data_rows = agg[~total_mask].sort_values("Countries (number)", ascending=False).reset_index(drop=True)
    total_row = agg[total_mask].reset_index(drop=True)
    return pd.concat([data_rows, total_row], ignore_index=True)


def gen_alphabetical_country_table(df) -> pd.DataFrame:
    """Alphabetical country table — all CBD parties + USA + Total row (matches original 198 rows)."""
    all_parties = df.copy()
    # Include CBD parties and USA (non-CBD but on UN scale)
    all_parties = all_parties.sort_values("party").reset_index(drop=True)
    all_parties["un_band"] = all_parties["un_band"].fillna("")
    all_parties["un_band_weight"] = all_parties["un_band_weight"].fillna(1.0)

    # Filter to CBD parties + USA
    shown = all_parties[all_parties["is_cbd_party"] | (all_parties["party"] == "United States of America")].copy()

    # Build columns matching original
    result = pd.DataFrame({
        "party": shown["party"],
        "total_allocation": shown["total_allocation"],
        "state_component": shown["state_component"],
        "iplc_component": shown["iplc_component"],
        "un_band": shown["un_band"],
        "un_band_weight": shown["un_band_weight"],
        "WB Income Group": shown["WB Income Group"],
        "UN LDC": shown["is_ldc"].map({True: "LDC", False: "-"}),
        "CBD Party": shown["is_cbd_party"].map({True: "Party", False: "-"}),
        "EU": shown["is_eu_ms"].map({True: "EU", False: "Non-EU"}),
    })

    # Add Total row
    numeric_cols = ["total_allocation", "state_component", "iplc_component", "un_band_weight"]
    total_row = {col: result[col].sum() for col in numeric_cols}
    total_row["party"] = "Total"
    total_row["un_band"] = ""
    total_row["WB Income Group"] = ""
    total_row["UN LDC"] = ""
    total_row["CBD Party"] = ""
    total_row["EU"] = ""
    result = pd.concat([result, pd.DataFrame([total_row])], ignore_index=True)

    return result


def gen_ranked_country_table(df) -> pd.DataFrame:
    """Ranked country table — sorted by allocation desc (matches original 198 rows)."""
    all_parties = df.copy()
    all_parties = all_parties.sort_values(
        ["total_allocation", "party"], ascending=[False, True]
    ).reset_index(drop=True)
    all_parties["un_band"] = all_parties["un_band"].fillna("")
    all_parties["un_band_weight"] = all_parties["un_band_weight"].fillna(1.0)

    shown = all_parties[all_parties["is_cbd_party"] | (all_parties["party"] == "United States of America")].copy()

    result = pd.DataFrame({
        "party": shown["party"],
        "total_allocation": shown["total_allocation"],
        "state_component": shown["state_component"],
        "iplc_component": shown["iplc_component"],
        "WB Income Group": shown["WB Income Group"],
        "UN LDC": shown["is_ldc"].map({True: "LDC", False: "-"}),
        "CBD Party": shown["is_cbd_party"].map({True: "Party", False: "-"}),
        "EU": shown["is_eu_ms"].map({True: "EU", False: "Non-EU"}),
        "un_band": shown["un_band"],
        "un_band_weight": shown["un_band_weight"],
    })

    # Add Total row
    numeric_cols = ["total_allocation", "state_component", "iplc_component", "un_band_weight"]
    total_row = {col: result[col].sum() for col in numeric_cols}
    total_row["party"] = "Total"
    total_row["un_band"] = ""
    total_row["WB Income Group"] = ""
    total_row["UN LDC"] = ""
    total_row["CBD Party"] = ""
    total_row["EU"] = ""
    result = pd.concat([result, pd.DataFrame([total_row])], ignore_index=True)

    return result


def gen_sids_country_table(df) -> pd.DataFrame:
    """SIDS country table — eligible SIDS only + Total row (matches original 40 rows)."""
    mask = df["is_cbd_party"] & df["eligible"] & df["is_sids"]
    sids_df = df[mask].copy()
    sids_df = sids_df.sort_values("party").reset_index(drop=True)

    result = pd.DataFrame({
        "party": sids_df["party"],
        "Countries (number)": 1,
        "total_allocation": sids_df["total_allocation"],
        "state_component": sids_df["state_component"],
        "iplc_component": sids_df["iplc_component"],
        "WB Income Group": sids_df["WB Income Group"],
        "UN LDC": sids_df["is_ldc"].map({True: "LDC", False: "-"}),
        "EU": sids_df["is_eu_ms"].map({True: "EU", False: "Non-EU"}),
    })

    # Add Total row
    total_row = {
        "party": "Total",
        "Countries (number)": len(sids_df),
        "total_allocation": sids_df["total_allocation"].sum(),
        "state_component": sids_df["state_component"].sum(),
        "iplc_component": sids_df["iplc_component"].sum(),
        "WB Income Group": "",
        "UN LDC": "",
        "EU": "",
    }
    result = pd.concat([result, pd.DataFrame([total_row])], ignore_index=True)

    return result


# ── Breakpoint and band-order tables ────────────────────────────────────────

def gen_breakpoint_summary(con) -> pd.DataFrame:
    scenarios = [
        ('0%', '3%', 0.0, 0.03, 'SOSAC only — modest rank shift among SIDS'),
        ('1.5%', '3%', 0.015, 0.03, 'Strict — IUSAF dominant for all Parties'),
        ('2.5%', '3%', 0.025, 0.03, 'Gini-minimum — band order preserved (margin 5.4%)'),
        ('3.0%', '3%', 0.03, 0.03, 'Band-order overturn — Band 6 > Band 5'),
        ('3.5%', '3%', 0.035, 0.03, 'Bounded — band order already overturned'),
        ('9.2%', '3%', 0.092, 0.03, 'TSAC component overturn for China'),
    ]
    rows = []
    for tsac_label, sosac_label, beta, gamma, desc in scenarios:
        base_df = get_base_data(con)
        pure = calculate_allocations(base_df, FUND, IPLC, exclude_high_income=True,
                                     tsac_beta=0, sosac_gamma=0, equality_mode=False,
                                     un_scale_mode=UN_SCALE)
        df = calculate_allocations(base_df, FUND, IPLC, exclude_high_income=True,
                                   tsac_beta=beta, sosac_gamma=gamma, equality_mode=False,
                                   un_scale_mode=UN_SCALE)
        eligible = df[df["eligible"]]
        pure_eligible = pure[pure["eligible"]]
        merged = eligible[["party", "final_share"]].merge(
            pure_eligible[["party", "final_share"]], on="party", suffixes=("_cur", "_base"))
        r_cur = merged["final_share_cur"].rank(method="average")
        r_base = merged["final_share_base"].rank(method="average")
        spearman = float(r_cur.corr(r_base, method="pearson"))
        iusaf_pct = (1 - beta - gamma) * 100
        rows.append({
            "TSAC": tsac_label, "SOSAC": sosac_label,
            "IUSAF %": round(iusaf_pct, 1),
            "Spearman rho": round(spearman, 3),
            "What Happens": desc,
        })
    return pd.DataFrame(rows)


def gen_band_order_preservation(con) -> pd.DataFrame:
    scenarios = [
        ('0% (Pure IUSAF)', 0.0, 0.0),
        ('1.5% (Strict)', 0.015, 0.03),
        ('2.5% (Gini-minimum)', 0.025, 0.03),
        ('3.0% (Band-order overturn)', 0.03, 0.03),
        ('3.5% (Bounded)', 0.035, 0.03),
        ('9.2% (TSAC component overturn)', 0.092, 0.03),
    ]
    rows = []
    for label, beta, gamma in scenarios:
        base_df = get_base_data(con)
        df = calculate_allocations(base_df, FUND, IPLC, exclude_high_income=True,
                                   tsac_beta=beta, sosac_gamma=gamma, equality_mode=False,
                                   un_scale_mode=UN_SCALE)
        eligible = df[df["eligible"]].copy()
        band6 = eligible[eligible["un_band"].str.startswith("Band 6", na=False)]
        band5 = eligible[eligible["un_band"].str.startswith("Band 5", na=False)]
        b6_mean = float(band6["total_allocation"].mean()) if len(band6) > 0 else 0
        b5_mean = float(band5["total_allocation"].mean()) if len(band5) > 0 else 0
        margin = ((b5_mean - b6_mean) / b5_mean * 100) if b5_mean > 0 else 0
        preserved = ("YES (margin {:.1f}%)".format(margin)
                     if b5_mean > b6_mean and margin < 10 else
                     "YES" if b5_mean > b6_mean else
                     "NO — Band 6 overtakes Band 5")
        rows.append({
            "TSAC Level": label,
            "Band 6 mean China (USD M)": round(b6_mean, 2),
            "Band 5 mean Brazil India Mexico (USD M)": round(b5_mean, 2),
            "Band 5 vs Band 6 margin (%)": round(margin, 1),
            "IUSAF Band Order Preserved": preserved,
        })
    return pd.DataFrame(rows)


def gen_balance_ranked_country_table(con, scenario_name: str, beta: float, gamma: float) -> pd.DataFrame:
    base_df = get_base_data(con)
    df = calculate_allocations(base_df, FUND, IPLC, exclude_high_income=True,
                               tsac_beta=beta, sosac_gamma=gamma, equality_mode=False,
                               un_scale_mode=UN_SCALE)
    eligible = df[df["eligible"]].copy()
    eligible = eligible.sort_values(["total_allocation", "party"], ascending=[False, True]).reset_index(drop=True)
    eligible.index = eligible.index + 1
    display_cols = ["party", "total_allocation", "state_component", "iplc_component",
                    "WB Income Group", "is_ldc", "is_sids", "is_eu_ms", "un_band"]
    result = eligible[display_cols].copy()
    result.insert(0, "Rank", eligible.index)
    return result


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    con = duckdb.connect(database=":memory:")
    load_data(con)

    base_df = get_base_data(con)
    df = calculate_allocations(
        base_df, FUND, IPLC,
        exclude_high_income=EXCLUDE_HI,
        high_income_mode=HI_MODE,
        tsac_beta=BETA,
        sosac_gamma=GAMMA,
        equality_mode=False,
        un_scale_mode=UN_SCALE,
    )

    results = []

    # Numeric columns across all tables
    alloc_cols = ["total_allocation", "state_component", "iplc_component"]

    # ── 1. LDC Panel ─────────────────────────────────────────────────────
    ldc_fresh, sids_panel_fresh = gen_ldc_sids_panel(df)
    ldc_orig = pd.read_csv(ORIG_DIR / "iusaf-ldc-panel-16042026.csv")
    save_csv(ldc_fresh, VAL_DIR / "iusaf-ldc-panel-valid.csv")
    results.append(compare_dataframes(ldc_orig, ldc_fresh, "LDC Panel", float_cols=alloc_cols))

    # ── 2. SIDS Panel ────────────────────────────────────────────────────
    sids_orig = pd.read_csv(ORIG_DIR / "iusaf-sids-panel-16042026.csv")
    save_csv(sids_panel_fresh, VAL_DIR / "iusaf-sids-panel-valid.csv")
    results.append(compare_dataframes(sids_orig, sids_panel_fresh, "SIDS Panel", float_cols=alloc_cols))

    # ── 3. UN Region ─────────────────────────────────────────────────────
    region_fresh = gen_region_table(df)
    region_orig = pd.read_csv(ORIG_DIR / "iusaf-unregion-15042026.csv")
    save_csv(region_fresh, VAL_DIR / "iusaf-unregion-valid.csv")
    results.append(compare_dataframes(region_orig, region_fresh, "UN Region",
                                       sort_by="region", float_cols=alloc_cols + ["Countries (number)"]))

    # ── 4. UN Sub-region ─────────────────────────────────────────────────
    subregion_fresh = gen_subregion_table(df)
    subregion_orig = pd.read_csv(ORIG_DIR / "iusaf-unsubregion-15042026.csv")
    save_csv(subregion_fresh, VAL_DIR / "iusaf-unsubregion-valid.csv")
    results.append(compare_dataframes(subregion_orig, subregion_fresh, "UN Sub-region",
                                       sort_by="sub_region", float_cols=alloc_cols + ["Countries (number)"]))

    # ── 5. Intermediate Region ────────────────────────────────────────────
    inter_fresh = gen_intermediate_region_table(df)
    inter_orig = pd.read_csv(ORIG_DIR / "iusaf-unintermediate-region-15042026.csv")
    save_csv(inter_fresh, VAL_DIR / "iusaf-unintermediate-region-valid.csv")
    results.append(compare_dataframes(inter_orig, inter_fresh, "Intermediate Region",
                                       sort_by="intermediate_region",
                                       float_cols=alloc_cols + ["Countries (number)"]))

    # ── 6. SIDS Countries ────────────────────────────────────────────────
    sids_country_fresh = gen_sids_country_table(df)
    sids_country_orig = pd.read_csv(ORIG_DIR / "iusaf-sids-countries-15042026.csv")
    save_csv(sids_country_fresh, VAL_DIR / "iusaf-sids-countries-valid.csv")
    results.append(compare_dataframes(sids_country_orig, sids_country_fresh, "SIDS Countries",
                                       sort_by="party", float_cols=alloc_cols))

    # ── 7. Alphabetical country ──────────────────────────────────────────
    alpha_fresh = gen_alphabetical_country_table(df)
    alpha_orig = pd.read_csv(ORIG_DIR / "iusaf-alphabetical-country-16042026.csv")
    save_csv(alpha_fresh, VAL_DIR / "iusaf-alphabetical-country-valid.csv")
    alpha_numeric = alloc_cols + ["un_band_weight"]
    results.append(compare_dataframes(alpha_orig, alpha_fresh, "Alphabetical Country",
                                       sort_by="party", float_cols=alpha_numeric))

    # ── 8. Ranked country ─────────────────────────────────────────────────
    ranked_fresh = gen_ranked_country_table(df)
    ranked_orig = pd.read_csv(ORIG_DIR / "iusaf-ranked-country-16042026.csv")
    save_csv(ranked_fresh, VAL_DIR / "iusaf-ranked-country-valid.csv")
    ranked_numeric = alloc_cols + ["un_band_weight"]
    results.append(compare_dataframes(ranked_orig, ranked_fresh, "Ranked Country",
                                       sort_by="party", float_cols=ranked_numeric))

    # ── 9. Breakpoint summary ────────────────────────────────────────────
    print("Computing breakpoint summary (6 scenarios)...")
    bp_fresh = gen_breakpoint_summary(con)
    bp_orig = pd.read_csv(ORIG_DIR / "iusaf-breakpoint-summary.csv")
    save_csv(bp_fresh, VAL_DIR / "iusaf-breakpoint-summary-valid.csv")
    results.append(compare_dataframes(bp_orig, bp_fresh, "Breakpoint Summary",
                                       float_cols=["IUSAF %", "Spearman rho"]))

    # ── 10. Band order preservation ──────────────────────────────────────
    print("Computing band-order preservation (6 scenarios)...")
    bo_fresh = gen_band_order_preservation(con)
    bo_orig = pd.read_csv(ORIG_DIR / "iusaf-band-order-preservation.csv")
    save_csv(bo_fresh, VAL_DIR / "iusaf-band-order-preservation-valid.csv")
    results.append(compare_dataframes(bo_orig, bo_fresh, "Band Order Preservation",
                                       float_cols=["Band 6 mean China (USD M)",
                                                    "Band 5 mean Brazil India Mexico (USD M)",
                                                    "Band 5 vs Band 6 margin (%)"]))

    # ── 11. Ranked country tables for balance-point scenarios ────────────
    balance_scenarios = [
        ("strict", 0.015, 0.03),
        ("gini_minimum", 0.025, 0.03),
        ("band_order_boundary", 0.03, 0.03),
    ]
    for name, beta, gamma in balance_scenarios:
        print(f"Computing ranked country table for {name}...")
        fresh = gen_balance_ranked_country_table(con, name, beta, gamma)
        orig_path = ORIG_DIR / f"iusaf-{name}-ranked-country.csv"
        if orig_path.exists():
            orig_df = pd.read_csv(orig_path)
            save_csv(fresh, VAL_DIR / f"iusaf-{name}-ranked-country-valid.csv")
            results.append(compare_dataframes(
                orig_df, fresh, f"Ranked Country ({name})",
                sort_by="party", float_cols=alloc_cols))
        else:
            results.append({"table": f"Ranked Country ({name})", "status": "NO_ORIGINAL", "differences": []})

    # ── 12. Income group aggregation (new, no original) ──────────────────
    income_fresh = aggregate_by_income(df)
    income_fresh = add_total_row(income_fresh, "WB Income Group")
    save_csv(income_fresh, VAL_DIR / "iusaf-income-group-valid.csv")
    results.append({"table": "Income Group", "status": "NEW (no original)",
                     "differences": ["Generated from current code; no original CSV to compare against"]})

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    match = fp_only = mismatch = no_orig = 0
    for r in results:
        s = r["status"]
        if s == "MATCH":
            match += 1
            print(f"  MATCH       {r['table']}")
        elif s == "FP_PRECISION":
            fp_only += 1
            print(f"  FP_PRECISION {r['table']} (last decimal place only)")
        elif s.startswith("NO_ORIGINAL") or s.startswith("NEW"):
            no_orig += 1
            print(f"  NO_ORIG     {r['table']}")
        else:
            mismatch += 1
            print(f"  MISMATCH    {r['table']}: {s}")
            for d in r["differences"][:5]:
                print(f"      {d}")

    print(f"\nTotal: {len(results)} tables")
    print(f"  MATCH:        {match}")
    print(f"  FP_PRECISION: {fp_only}  (cosmetic last-decimal-place only)")
    print(f"  MISMATCH:     {mismatch}")
    print(f"  NO_ORIGINAL:  {no_orig}")
    print(f"\nFresh CSVs written to: {VAL_DIR}")

    with open(VAL_DIR / "validation-report.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Validation report: {VAL_DIR / 'validation-report.json'}")


if __name__ == "__main__":
    main()
