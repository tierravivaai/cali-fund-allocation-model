import pytest
import pandas as pd
import duckdb
from logic.data_loader import load_data, get_base_data
from logic.calculator import calculate_allocations, aggregate_by_income

@pytest.fixture
def mock_con():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    return con

def test_aggregate_by_income_sums(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50)
    
    income_df = aggregate_by_income(results_df)
    
    # Check that the sum of all income groups equals the total fund size (in millions)
    assert pytest.approx(income_df['total_allocation'].sum(), 0.001) == 1000
    
    # "Not Available" group should no longer exist as all Parties have been mapped
    # (except for EU which is now handled separately or mapped to High Income)
    assert "Not Available" not in income_df['WB Income Group'].values

def test_aggregate_by_income_structure(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    income_df = aggregate_by_income(results_df)
    
    required_cols = ['WB Income Group', 'total_allocation', 'state_envelope', 'iplc_envelope']
    for col in required_cols:
        assert col in income_df.columns
