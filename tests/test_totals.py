import pytest
import pandas as pd
import duckdb
from logic.data_loader import load_data, get_base_data
from logic.calculator import calculate_allocations, aggregate_by_region, aggregate_by_income, add_total_row

@pytest.fixture
def mock_con():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    return con

def test_add_total_row_logic():
    df = pd.DataFrame({
        'name': ['A', 'B'],
        'count': [10, 20],
        'value': [1.5, 2.5]
    })
    
    total_df = add_total_row(df, 'name')
    
    assert len(total_df) == 3
    assert total_df.iloc[-1]['name'] == 'Total'
    assert total_df.iloc[-1]['count'] == 30
    assert total_df.iloc[-1]['value'] == 4.0

def test_region_total_sum(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    region_agg = aggregate_by_region(results_df, "region")
    total_region = add_total_row(region_agg, "region")
    
    total_countries = total_region.iloc[-1]['Countries (number)']
    total_allocation = total_region.iloc[-1]['total_allocation']
    
    # 196 CBD Parties total
    assert total_countries == 196
    # Total allocation should match fund size (in millions)
    assert pytest.approx(total_allocation, 0.01) == 1000.0

def test_income_total_sum(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    income_agg = aggregate_by_income(results_df)
    total_income = add_total_row(income_agg, "WB Income Group")
    
    total_countries = total_income.iloc[-1]['Countries (number)']
    assert total_countries == 196
    assert pytest.approx(total_income.iloc[-1]['total_allocation'], 0.01) == 1000.0

def test_ldc_sids_total_sum(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    # Simulate the manual LDC/SIDS summary logic from app.py
    from logic.calculator import aggregate_special_groups
    ldc_total, sids_total = aggregate_special_groups(results_df)
    
    # LDC summary validation
    mask_cbd = results_df['is_cbd_party']
    non_ldc_df = results_df[mask_cbd & (~results_df['is_ldc'])]
    non_ldc_count = len(non_ldc_df)
    
    total_countries_ldc_view = ldc_total['Countries (number)'] + non_ldc_count
    assert total_countries_ldc_view == 196

    # SIDS summary validation
    non_sids_df = results_df[mask_cbd & (~results_df['is_sids'])]
    non_sids_count = len(non_sids_df)
    
    total_countries_sids_view = sids_total['Countries (number)'] + non_sids_count
    assert total_countries_sids_view == 196

def test_party_tab_total_sum(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    # Simulate tab1 filtering (no search)
    filtered_df = results_df.copy()
    total_df = add_total_row(filtered_df, "party")
    
    total_allocation = total_df.iloc[-1]['total_allocation']
    assert pytest.approx(total_allocation, 0.01) == 1000.0

def test_intermediate_region_total_sum(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    # Aggregator should include 'NA'
    int_region_agg = aggregate_by_region(results_df, "intermediate_region")
    total_int_region = add_total_row(int_region_agg, "intermediate_region")
    
    total_countries = total_int_region.iloc[-1]['Countries (number)']
    assert total_countries == 196
    assert pytest.approx(total_int_region.iloc[-1]['total_allocation'], 0.01) == 1000.0

def test_aggregation_column_order(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    # Check By Region
    region_agg = aggregate_by_region(results_df, "region")
    # In app.py we use: ["region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    # Here we check if the expected columns exist and can be ordered
    cols = list(region_agg.columns)
    # The aggregator returns ['region', 'total_allocation', 'state_component', 'iplc_component', 'Countries (number)']
    # We want to ensure it is in the dataframe that is displayed.
    # Actually, we should test the reordering logic itself or just that the column exists to be reordered.
    assert "Countries (number)" in cols
    
    # Test the specific reordering logic used in app.py
    display_cols = ["region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    reordered = region_agg[display_cols]
    assert list(reordered.columns)[1] == "Countries (number)"

def test_detail_tab_country_counts(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    # Low Income Detail
    li_df = results_df[results_df['WB Income Group'] == 'Low income'].copy()
    li_table = li_df.copy()
    li_table.insert(1, "Countries (number)", 1)
    total_li = add_total_row(li_table, "party")
    
    # Total row should show sum of '1's
    assert total_li.iloc[-1]['Countries (number)'] == len(li_df)
