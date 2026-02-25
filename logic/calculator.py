import pandas as pd

def _apply_floor_ceiling_shares(weights: pd.Series, floor: float, cap: float) -> pd.Series:
    w = weights.fillna(0.0).clip(lower=0.0)
    idx = w.index.tolist()
    n = len(idx)

    if n == 0:
        return pd.Series(dtype=float)

    floor = max(0.0, float(floor))
    cap = min(1.0, float(cap))

    if floor > cap:
        floor = cap

    if floor * n > 1.0:
        return pd.Series(1.0 / n, index=idx)

    if cap * n < 1.0:
        return pd.Series(1.0 / n, index=idx)

    fixed_low = set()
    fixed_high = set()

    while True:
        free = [i for i in idx if i not in fixed_low and i not in fixed_high]

        remaining = 1.0 - floor * len(fixed_low) - cap * len(fixed_high)
        remaining = max(0.0, remaining)

        shares = pd.Series(0.0, index=idx)

        if fixed_low:
            shares.loc[list(fixed_low)] = floor

        if fixed_high:
            shares.loc[list(fixed_high)] = cap

        if free:
            denom = w.loc[free].sum()
            if denom <= 0:
                shares.loc[free] = remaining / len(free)
            else:
                shares.loc[free] = remaining * (w.loc[free] / denom)

        new_low = set(shares.loc[free][shares.loc[free] < floor - 1e-12].index)
        new_high = set(shares.loc[free][shares.loc[free] > cap + 1e-12].index)

        if not new_low and not new_high:
            s = shares.sum()
            return shares / s if s > 0 else shares

        fixed_low |= new_low
        fixed_high |= new_high

def calculate_allocations(
    df,
    fund_size,
    iplc_share_pct,
    show_raw_inversion=False,
    exclude_high_income=False,
    floor_pct=0.0,
    ceiling_pct=None,
):
    # Filter out parties with 0 share for inversion logic (except for display later)
    # But for Cali Fund, we need to invert the non-zero ones.
    
    calc_df = df.copy()
    
    # 1. Define eligibility
    calc_df["eligible"] = calc_df["is_cbd_party"]
    if exclude_high_income:
        # Explicitly exclude "High income" countries among CBD Parties
        calc_df["eligible"] = calc_df["eligible"] & (calc_df["WB Income Group"] != "High income")
    
    # Inversion logic: only for eligible parties with shares > 0
    # The source 'un_share' is expressed as a percentage (e.g. 5.469)
    # First convert it to a fraction by dividing by 100.
    mask = calc_df["eligible"] & (calc_df['un_share'] > 0) & (calc_df['un_share'].notna())
    
    calc_df.loc[mask, 'un_share_fraction'] = calc_df.loc[mask, 'un_share'] / 100.0
    calc_df.loc[mask, 'inv_weight'] = 1.0 / calc_df.loc[mask, 'un_share_fraction']
    
    calc_df.loc[~mask, 'un_share_fraction'] = 0.0
    calc_df.loc[~mask, 'inv_weight'] = 0.0
    
    calc_df["inverted_share"] = 0.0

    eligible_mask = calc_df["eligible"] & (calc_df["un_share"] > 0) & (calc_df["un_share"].notna())
    eligible_idx = calc_df.index[eligible_mask]

    if len(eligible_idx) > 0:
        floor = float(floor_pct) / 100.0
        cap = 1.0 if ceiling_pct is None else float(ceiling_pct) / 100.0

        constrained_shares = _apply_floor_ceiling_shares(
            calc_df.loc[eligible_idx, "inv_weight"],
            floor=floor,
            cap=cap
        )

        calc_df.loc[eligible_idx, "inverted_share"] = constrained_shares
        
    calc_df['total_allocation'] = calc_df['inverted_share'] * fund_size
    calc_df['iplc_component'] = calc_df['total_allocation'] * (iplc_share_pct / 100.0)
    calc_df['state_component'] = calc_df['total_allocation'] - calc_df['iplc_component']
    
    # Convert to millions for display
    for col in ['total_allocation', 'iplc_component', 'state_component']:
        calc_df[col] = calc_df[col] / 1_000_000.0
        
    return calc_df

def aggregate_by_region(df, region_col='region'):
    # We count all CBD parties that are eligible for the calculation
    # Even if they have 0 allocation (e.g. they had 0 UN share or are the EU entity)
    # BUT we only show those that are "eligible" based on the current toggle (e.g. not HI if excluded)
    mask = df['is_cbd_party'] & df['eligible']
    
    agg_sums = df[mask].groupby(region_col, dropna=False)[['total_allocation', 'state_component', 'iplc_component']].sum()
    agg_counts = df[mask].groupby(region_col, dropna=False)['party'].count()
    
    agg = agg_sums.merge(agg_counts, left_index=True, right_index=True).reset_index()
    agg = agg.rename(columns={'party': 'Countries (number)'})
    
    # Filter to only show groups that have at least one party
    return agg[agg['Countries (number)'] > 0]

def aggregate_eu(df):
    ms_df = df[df['is_eu_ms']]
    eu_party = df[df['party'] == 'European Union']
    
    combined = pd.concat([ms_df, eu_party])
    total_row = combined[['total_allocation', 'state_component', 'iplc_component']].sum()
    total_row['party'] = 'EU Member States + European Union (total)'
    total_row['Countries (number)'] = len(combined)
    
    return combined, total_row

def aggregate_special_groups(df):
    # Count all CBD parties in these groups that are eligible
    mask = df['is_cbd_party'] & df['eligible']
    
    ldc_df = df[df['is_ldc'] & mask]
    sids_df = df[df['is_sids'] & mask]
    
    ldc_sum = ldc_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    ldc_sum['Countries (number)'] = len(ldc_df)
    
    sids_sum = sids_df[['total_allocation', 'state_component', 'iplc_component']].sum()
    sids_sum['Countries (number)'] = len(sids_df)
    
    return ldc_sum, sids_sum

def aggregate_by_income(df):
    # Count all CBD parties that are eligible
    mask = df['is_cbd_party'] & df['eligible']
    
    agg_sums = df[mask].groupby('WB Income Group', dropna=False)[['total_allocation', 'state_component', 'iplc_component']].sum()
    agg_counts = df[mask].groupby('WB Income Group', dropna=False)['party'].count()
    
    agg = agg_sums.merge(agg_counts, left_index=True, right_index=True).reset_index()
    agg = agg.rename(columns={'party': 'Countries (number)'})
    
    return agg[agg['Countries (number)'] > 0]

def add_total_row(df, label_col, label="Total"):
    """Adds a summary 'Total' row to an aggregated dataframe."""
    if df.empty:
        return df
        
    numeric_cols = df.select_dtypes(include=['number']).columns
    total_row = df[numeric_cols].sum()
    
    # Create the new row as a dictionary
    row_dict = {col: total_row[col] for col in numeric_cols}
    row_dict[label_col] = label
    
    # Fill in any missing columns with empty string or appropriate default
    for col in df.columns:
        if col not in row_dict:
            row_dict[col] = ""
            
    return pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)
