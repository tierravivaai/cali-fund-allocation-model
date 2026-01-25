from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Dict, Optional

import duckdb
import pandas as pd


DEFAULT_PARAMS = {
    "fund_usd": 1_000_000_000,
    "iplc_share": 0.5,
    "smoothing_exponent": 0.5,
    "pct_lower_bound": 0.01,
    "cap_share": 0.02,
    "blend_baseline_share": 0.2,
    "baseline_recipient": "developing",
}


def _render_sql(sql_text: str, params: Dict[str, Any]) -> str:
    rendered = sql_text
    for key, value in params.items():
        if key == "baseline_recipient":
            replacement = f"'{value}'"
        else:
            replacement = str(value)
        pattern = r"\{\{\s*" + re.escape(key) + r"[^}]*\}\}"
        rendered = re.sub(pattern, replacement, rendered)
    return rendered


def _load_cbd_contributions(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(
        columns={
            "Party": "party",
            "CBD_scale_with_ceiling_percentage": "cbd_scale_pct",
        }
    )
    df["party"] = df["party"].astype(str).str.strip()
    df = df[df["party"].notna() & (df["party"].str.lower() != "total")]
    df["cbd_scale_pct"] = pd.to_numeric(df["cbd_scale_pct"], errors="coerce")
    df["is_party"] = True
    df["source_decision"] = "CBD/COP/DEC/16/28"
    return df[["party", "cbd_scale_pct", "is_party", "source_decision"]]


def _load_unsd_m49(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(
        columns={
            "Country or Area": "party",
            "Region Name": "un_region",
            "Sub-region Name": "un_subregion",
            "Intermediate Region Name": "un_intermediate",
        }
    )
    df["party"] = df["party"].astype(str).str.strip()
    dev_status = pd.Series([None] * len(df))
    for col in [
        "Least Developed Countries (LDC)",
        "Land Locked Developing Countries (LLDC)",
        "Small Island Developing States (SIDS)",
    ]:
        if col in df.columns:
            is_dev = df[col].notna() & (df[col].astype(str).str.upper() != "NA")
            dev_status = dev_status.where(~is_dev, "developing")
    df["dev_status"] = dev_status
    return df[["party", "un_region", "un_subregion", "un_intermediate", "dev_status"]]


def _load_eu27(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["party"] = df["party"].astype(str).str.strip()
    df["is_eu27"] = df["is_eu27"].astype(str).str.upper() == "TRUE"
    return df[["party", "is_eu27"]]


def _load_manual_name_map(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df[["party_raw", "party_mapped"]]


def build_database(
    db_path: Path,
    inputs_dir: Path,
    sql_path: Path,
    outputs_dir: Path,
    params: Optional[Dict[str, Any]] = None,
) -> None:
    inputs_dir = inputs_dir.resolve()
    outputs_dir.mkdir(parents=True, exist_ok=True)
    params = {**DEFAULT_PARAMS, **(params or {})}

    cbd_path = inputs_dir / "cbd_cop16_budget_table.csv"
    unsd_path = inputs_dir / "unsd_region_useme.csv"
    eu_path = inputs_dir / "eu27.csv"
    name_map_path = inputs_dir / "manual_name_map.csv"

    cbd_df = _load_cbd_contributions(cbd_path)
    unsd_df = _load_unsd_m49(unsd_path)
    eu_df = _load_eu27(eu_path)

    con = duckdb.connect(str(db_path))
    con.register("cbd_assessed_contributions_df", cbd_df)
    con.register("unsd_m49_df", unsd_df)
    con.register("eu27_df", eu_df)

    con.execute("CREATE OR REPLACE TABLE cbd_assessed_contributions AS SELECT * FROM cbd_assessed_contributions_df")
    con.execute("CREATE OR REPLACE TABLE unsd_m49 AS SELECT * FROM unsd_m49_df")
    con.execute("CREATE OR REPLACE TABLE eu27 AS SELECT * FROM eu27_df")

    if name_map_path.exists():
        name_map_df = _load_manual_name_map(name_map_path)
    else:
        name_map_df = pd.DataFrame(
            {
                "party_raw": pd.Series(dtype="string"),
                "party_mapped": pd.Series(dtype="string"),
            }
        )
    con.register("manual_name_map_df", name_map_df)
    con.execute("CREATE OR REPLACE TABLE manual_name_map AS SELECT * FROM manual_name_map_df")

    sql_text = sql_path.read_text()
    rendered_sql = _render_sql(sql_text, params)
    con.execute(rendered_sql)

    export_views = [
        "v_alloc_country",
        "v_alloc_region",
        "v_alloc_subregion",
        "v_alloc_intermediate",
        "v_alloc_eu",
        "v_alloc_eu_total",
        "v_alloc_devstatus",
    ]
    for view in export_views:
        output_path = outputs_dir / f"{view}.csv"
        con.execute(
            "COPY (SELECT * FROM "
            + view
            + ") TO ? WITH (HEADER, DELIMITER ',')",
            [str(output_path)],
        )
    con.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Cali Fund DuckDB outputs.")
    parser.add_argument("--db", default="cali_fund.duckdb", help="Path to DuckDB file")
    parser.add_argument("--inputs-dir", default="data-raw", help="Path to input CSVs")
    parser.add_argument("--outputs-dir", default="data", help="Path for output tables")
    parser.add_argument("--sql-path", default="model/allocation.sql", help="Path to model SQL")
    parser.add_argument("--fund-usd", type=float, default=DEFAULT_PARAMS["fund_usd"])
    parser.add_argument("--iplc-share", type=float, default=DEFAULT_PARAMS["iplc_share"])
    parser.add_argument("--smoothing-exponent", type=float, default=DEFAULT_PARAMS["smoothing_exponent"])
    parser.add_argument("--pct-lower-bound", type=float, default=DEFAULT_PARAMS["pct_lower_bound"])
    parser.add_argument("--cap-share", type=float, default=DEFAULT_PARAMS["cap_share"])
    parser.add_argument("--blend-baseline-share", type=float, default=DEFAULT_PARAMS["blend_baseline_share"])
    parser.add_argument("--baseline-recipient", default=DEFAULT_PARAMS["baseline_recipient"])
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    params = {
        "fund_usd": args.fund_usd,
        "iplc_share": args.iplc_share,
        "smoothing_exponent": args.smoothing_exponent,
        "pct_lower_bound": args.pct_lower_bound,
        "cap_share": args.cap_share,
        "blend_baseline_share": args.blend_baseline_share,
        "baseline_recipient": args.baseline_recipient,
    }
    build_database(
        db_path=Path(args.db),
        inputs_dir=Path(args.inputs_dir),
        sql_path=Path(args.sql_path),
        outputs_dir=Path(args.outputs_dir),
        params=params,
    )


if __name__ == "__main__":
    main()
