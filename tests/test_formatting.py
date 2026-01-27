import pandas as pd

def format_currency(val, use_thousands):
    if use_thousands and val < 1.0:
        return f"${val * 1000:,.2f}k"
    return f"${val:,.2f}m"

def test_currency_formatting_millions():
    # When use_thousands is False, everything should be in 'm'
    assert format_currency(1.5, False) == "$1.50m"
    assert format_currency(0.5, False) == "$0.50m"
    assert format_currency(1234.56, False) == "$1,234.56m"

def test_currency_formatting_thousands():
    # When use_thousands is True, values < 1.0 should be in 'k'
    assert format_currency(1.5, True) == "$1.50m"
    assert format_currency(0.5, True) == "$500.00k"
    assert format_currency(0.001, True) == "$1.00k"
    assert format_currency(1234.56, True) == "$1,234.56m"

def test_sorting_preservation_logic():
    # This simulates the logic in app.py:
    # If use_thousands is False, we DON'T apply format_currency to the dataframe
    # but let st.column_config.NumberColumn handle it.
    
    data = {'total_allocation': [10.5, 2.1, 15.0]}
    df = pd.DataFrame(data)
    
    # Simulate sorting by Total USD descending
    sorted_df = df.sort_values('total_allocation', ascending=False)
    
    assert list(sorted_df['total_allocation']) == [15.0, 10.5, 2.1]
    # In the app, this numeric df is passed to st.dataframe with NumberColumn
    # which ensures correct numeric sorting in the UI.
