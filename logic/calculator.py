import pandas as pd

def calculate_allocations(df, fund_size, iplc_share_pct, show_raw_inversion=False):
    # Filter out parties with 0 share for inversion logic (except for display later)
    # But for Cali Fund, we need to invert the non-zero ones.
    
    calc_df = df.copy()
    
    # Inversion logic: only for shares > 0
    # The source 'un_share' is expressed as a percentage (e.g. 5.469)
    # First convert it to a fraction by dividing by 100.
    mask = (calc_df['un_share'] > 0) & (calc_df['un_share'].notna())
    
    calc_df.loc[mask, 'un_share_fraction'] = calc_df.loc[mask, 'un_share'] / 100.0
    calc_df.loc[mask, 'inv_weight'] = 1.0 / calc_df.loc[mask, 'un_share_fraction']
    
    calc_df.loc[~mask, 'un_share_fraction'] = 0.0
    calc_df.loc[~mask, 'inv_weight'] = 0.0
    
    total_inv_weight = calc_df['inv_weight'].sum()
    
    if total_inv_weight > 0:
        # Normalize: inverse weight / sum(inverse weights)
        # These normalized shares will sum to 1.0
        calc_df['inverted_share'] = calc_df['inv_weight'] / total_inv_weight
    else:
        calc_df['inverted_share'] = 0.0
        
    calc_df['total_allocation'] = calc_df['inverted_share'] * fund_size
    calc_df['iplc_envelope'] = calc_df['total_allocation'] * (iplc_share_pct / 100.0)
    calc_df['state_envelope'] = calc_df['total_allocation'] - calc_df['iplc_envelope']
    
    # Convert to millions for display
    for col in ['total_allocation', 'iplc_envelope', 'state_envelope']:
        calc_df[col] = calc_df[col] / 1_000_000.0
        
    return calc_df

def aggregate_by_region(df, region_col='region'):
    return df.groupby(region_col)[['total_allocation', 'iplc_envelope', 'state_envelope']].sum().reset_index()

def aggregate_eu(df):
    ms_df = df[df['is_eu_ms']]
    eu_party = df[df['party'] == 'European Union']
    
    combined = pd.concat([ms_df, eu_party])
    total_row = combined[['total_allocation', 'iplc_envelope', 'state_envelope']].sum()
    total_row['party'] = 'EU Member States + European Union (total)'
    
    return combined, total_row

def aggregate_special_groups(df):
    ldc = df[df['is_ldc']][['total_allocation', 'iplc_envelope', 'state_envelope']].sum()
    sids = df[df['is_sids']][['total_allocation', 'iplc_envelope', 'state_envelope']].sum()
    
    return ldc, sids
