"""Tests for reference parameters and reset functionality."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from scripts.run_duckdb import DEFAULT_PARAMS  # noqa: E402


def test_reference_params_exist() -> None:
    """Test that reference parameters exist and have expected values."""
    # Reference scenario parameters (from OBJECTIVES.md)
    expected_params = {
        "fund_usd": 1_000_000_000,
        "iplc_share": 0.5,
        "smoothing_exponent": 0.5,
        "pct_lower_bound": 0.01,
        "cap_share": 0.02,
        "blend_baseline_share": 0.2,
        "baseline_recipient": "least developed countries (LDC)",
    }
    
    # Verify DEFAULT_PARAMS matches expected reference values
    assert DEFAULT_PARAMS == expected_params, f"DEFAULT_PARAMS do not match expected reference values.\nExpected: {expected_params}\nActual: {DEFAULT_PARAMS}"


def test_iplc_share_minimum_50_percent() -> None:
    """Test that IPLC share is at least 50% (0.5) as per requirements."""
    assert DEFAULT_PARAMS["iplc_share"] >= 0.5, "IPLC share must be at least 50%"


def test_fund_size_positive() -> None:
    """Test that fund size is positive."""
    assert DEFAULT_PARAMS["fund_usd"] > 0, "Fund size must be positive"


def test_smoothing_exponent_positive() -> None:
    """Test that smoothing exponent is positive."""
    assert DEFAULT_PARAMS["smoothing_exponent"] > 0, "Smoothing exponent must be positive"


def test_percent_bound_positive() -> None:
    """Test that percent lower bound is positive."""
    assert DEFAULT_PARAMS["pct_lower_bound"] > 0, "Percent lower bound must be positive"


def test_cap_share_positive_and_reasonable() -> None:
    """Test that cap share is positive and less than 1 (100%)."""
    assert DEFAULT_PARAMS["cap_share"] > 0, "Cap share must be positive"
    assert DEFAULT_PARAMS["cap_share"] < 1, "Cap share must be less than 100%"


def test_baseline_blend_between_0_and_1() -> None:
    """Test that baseline blend share is between 0 and 1."""
    assert 0 <= DEFAULT_PARAMS["blend_baseline_share"] <= 1, "Baseline blend share must be between 0 and 1"


def test_baseline_recipient_valid() -> None:
    """Test that baseline recipient is a valid string."""
    assert DEFAULT_PARAMS["baseline_recipient"] in [
        "least developed countries (LDC)",
        "all"
    ], "Baseline recipient must be either 'least developed countries (LDC)' or 'all'"
