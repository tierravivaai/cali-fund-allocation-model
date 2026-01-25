from __future__ import annotations

import sys
import warnings
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from scripts.run_duckdb import DEFAULT_PARAMS, build_database  # noqa: E402


def test_allocations_reconcile(tmp_path: Path) -> None:
    db_path = tmp_path / "test_cali_fund.duckdb"
    outputs_dir = tmp_path / "outputs"
    build_database(
        db_path=db_path,
        inputs_dir=PROJECT_ROOT / "data-raw",
        sql_path=PROJECT_ROOT / "model" / "allocation.sql",
        outputs_dir=outputs_dir,
        params=DEFAULT_PARAMS,
    )

    con = duckdb.connect(str(db_path))
    total_share = con.execute("SELECT SUM(share_final) FROM v_alloc_country").fetchone()[0]
    assert total_share is not None
    assert abs(total_share - 1.0) < 1e-6

    fund_usd = DEFAULT_PARAMS["fund_usd"]
    total_alloc = con.execute("SELECT SUM(alloc_usd) FROM v_alloc_country").fetchone()[0]
    assert total_alloc is not None
    assert abs(total_alloc - fund_usd) < 1e-2

    split_check = con.execute(
        "SELECT MAX(ABS((iplc_usd + state_usd) - alloc_usd)) FROM v_alloc_country"
    ).fetchone()[0]
    assert split_check is not None
    assert split_check < 1e-6

    cap_share = DEFAULT_PARAMS["cap_share"]
    max_share = con.execute("SELECT MAX(share_final) FROM v_alloc_country").fetchone()[0]
    assert max_share is not None
    assert max_share <= cap_share + 1e-9

    missing_regions = con.execute(
        "SELECT COUNT(*) FROM v_alloc_country WHERE un_region IS NULL"
    ).fetchone()[0]
    if missing_regions and missing_regions > 0:
        warnings.warn(f"{missing_regions} parties missing UN region mappings")

    con.close()
