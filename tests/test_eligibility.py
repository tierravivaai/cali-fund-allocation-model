import pytest
import pandas as pd
import duckdb
from logic.data_loader import load_data, get_base_data
from logic.calculator import calculate_allocations

@pytest.fixture
def mock_con():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    return con

def test_eligibility_filter_high_income(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000 # 1bn
    
    # Toggle ON: Exclude High Income
    results_filtered = calculate_allocations(base_df, fund_size, 50, exclude_high_income=True)
    
    # Check that High income countries have 0 allocation
    hi_countries = results_filtered[results_filtered['income_group'] == 'High income']
    assert (hi_countries['total_allocation'] == 0).all()
    
    # Check that non-High income countries have > 0 allocation (if un_share > 0)
    eligible_countries = results_filtered[(results_filtered['income_group'] != 'High income') & (results_filtered['un_share'] > 0)]
    assert (eligible_countries['total_allocation'] > 0).all()
    
    # Check sum consistency
    assert pytest.approx(results_filtered['total_allocation'].sum(), 0.001) == 1000

def test_eligibility_toggle_off(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # Toggle OFF: Include everyone
    results_all = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    # High income countries should have > 0 allocation
    hi_countries = results_all[(results_all['income_group'] == 'High income') & (results_all['un_share'] > 0)]
    assert (hi_countries['total_allocation'] > 0).all()
    
    # Check sum consistency
    assert pytest.approx(results_all['total_allocation'].sum(), 0.001) == 1000
