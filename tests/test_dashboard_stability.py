import pytest
import pandas as pd
import numpy as np

def test_top_10_consistency_with_ties():
    # Simulate a tie situation
    data = {
        'party': ['A-Country', 'B-Country', 'C-Country', 'D-Country', 'E-Country', 'F-Country', 'G-Country', 'H-Country', 'I-Country', 'J-Country', 'K-Country', 'L-Country'],
        'current_amt': [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
    }
    df = pd.DataFrame(data)
    
    # Requirement: Top 10 in alphabetical order when tied
    # Stable sort by party, then by amount
    df_sorted = df.sort_values(by=['current_amt', 'party'], ascending=[False, True])
    top_10 = df_sorted.head(10)
    
    # Check alphabetical order
    expected_parties = sorted(data['party'])[:10]
    assert list(top_10['party']) == expected_parties

def test_bottom_10_consistency_with_ties():
    # Simulate a tie situation
    data = {
        'party': ['A-Country', 'B-Country', 'C-Country', 'D-Country', 'E-Country', 'F-Country', 'G-Country', 'H-Country', 'I-Country', 'J-Country', 'K-Country', 'L-Country'],
        'current_amt': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    }
    df = pd.DataFrame(data)
    
    # Requirement: Bottom 10 in alphabetical order when tied
    # For Bottom 10 (ascending amount), tie-break should also be consistent (alphabetical)
    df_sorted = df.sort_values(by=['current_amt', 'party'], ascending=[True, True])
    bottom_10 = df_sorted.head(10)
    
    # Check alphabetical order
    expected_parties = sorted(data['party'])[:10]
    assert list(bottom_10['party']) == expected_parties
