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

def test_middle_income_tab_logic(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Logic from app.py: Middle Income includes 'Lower middle income' and 'Upper middle income'
    mi_df = results_df[results_df['World Bank Income Group'].isin(['Lower middle income', 'Upper middle income'])]
    
    # Check if all included rows belong to those groups
    assert all(mi_df['World Bank Income Group'].isin(['Lower middle income', 'Upper middle income']))
    # Verify both groups are represented (given our standard dataset)
    assert 'Lower middle income' in mi_df['World Bank Income Group'].values
    assert 'Upper middle income' in mi_df['World Bank Income Group'].values
    
def test_high_income_tab_logic(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Logic from app.py: High Income tab
    hi_df = results_df[results_df['World Bank Income Group'] == 'High income']
    
    # Check all included rows are High income
    assert all(hi_df['World Bank Income Group'] == 'High income')
    assert 'High income' in hi_df['World Bank Income Group'].values

def test_allocation_sorting_logic(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Default sort from app.py: Allocation (highest first) then party (A-Z)
    sorted_df = results_df.sort_values(
        by=["total_allocation", "party"],
        ascending=[False, True]
    )
    
    # First row should have the maximum allocation
    assert sorted_df.iloc[0]['total_allocation'] == results_df['total_allocation'].max()
    
    # Check monotonic decreasing (mostly) - if allocations are equal, party name is sorted alphabetically
    allocations = sorted_df['total_allocation'].tolist()
    assert all(allocations[i] >= allocations[i+1] for i in range(len(allocations)-1))

def test_alphabetical_sorting_logic(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # A-Z sort from app.py
    sorted_df = results_df.sort_values(by="party", ascending=True)
    
    parties = sorted_df['party'].tolist()
    assert parties == sorted(parties)
