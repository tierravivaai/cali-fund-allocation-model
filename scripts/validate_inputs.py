from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import pandas as pd


REQUIRED_COLUMNS: Dict[str, List[str]] = {
    "cbd_cop16_budget_table.csv": ["Party", "CBD_scale_with_ceiling_percentage"],
    "unsd_region_useme.csv": [
        "Country or Area",
        "Region Name",
        "Sub-region Name",
        "Intermediate Region Name",
    ],
    "eu27.csv": ["party", "is_eu27"],
}


def _check_file(path: Path, required: List[str]) -> List[str]:
    df = pd.read_csv(path, nrows=1)
    missing = [col for col in required if col not in df.columns]
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate input CSV schemas.")
    parser.add_argument("--inputs-dir", default="data-raw", help="Path to input CSVs")
    args = parser.parse_args()

    inputs_dir = Path(args.inputs_dir)
    missing_any = False
    for filename, required_cols in REQUIRED_COLUMNS.items():
        path = inputs_dir / filename
        if not path.exists():
            missing_any = True
            print(f"Missing input file: {filename}")
            continue
        missing = _check_file(path, required_cols)
        if missing:
            missing_any = True
            print(f"{filename} missing columns: {', '.join(missing)}")
        else:
            print(f"{filename}: OK")

    if missing_any:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
