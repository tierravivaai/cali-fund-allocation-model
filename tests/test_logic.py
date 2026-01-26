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

def test_allocation_sums_to_fund_size(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000 # 1bn
    results = calculate_allocations(base_df, fund_size, 50)
    
    # Sum of total_allocation should be 1000 (millions)
    assert pytest.approx(results['total_allocation'].sum(), 0.001) == 1000

def test_iplc_state_consistency(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results = calculate_allocations(base_df, fund_size, 60)
    
    # iplc + state should equal total
    check = results['iplc_envelope'] + results['state_envelope']
    pd.testing.assert_series_equal(check, results['total_allocation'], check_names=False)
    
    # iplc should be 60% of total
    assert pytest.approx(results['iplc_envelope'].sum(), 0.001) == 600

def test_eu_party_exists(mock_con):
    base_df = get_base_data(mock_con)
    assert 'European Union' in base_df['party'].values
    eu_share = base_df[base_df['party'] == 'European Union']['un_share'].values[0]
    assert eu_share == 0.0

def test_cbd_party_count(mock_con):
    base_df = get_base_data(mock_con)
    
    # 1. Count Parties in the source CSV
    # (Verified via pandas script as 196 including European Union)
    source_count = 196 
    
    # 2. Count is_cbd_party = True in our processed dataframe
    calculated_count = base_df['is_cbd_party'].sum()
    
    # These should match exactly
    assert calculated_count == source_count
    
    # 3. Ensure EU is marked as a CBD Party
    eu_cbd_status = base_df[base_df['party'] == 'European Union']['is_cbd_party'].values[0]
    assert eu_cbd_status == True


