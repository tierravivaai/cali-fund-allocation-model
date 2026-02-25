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
    ceiling_pct=10.0,
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
        cap = float(ceiling_pct) / 100.0

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
    agg = df.groupby(region_col, dropna=False)[['total_allocation', 'state_component', 'iplc_component']].sum().reset_index()
    return agg[agg['total_allocation'] > 0]

def aggregate_eu(df):
    ms_df = df[df['is_eu_ms']]
    eu_party = df[df['party'] == 'European Union']
    
    combined = pd.concat([ms_df, eu_party])
    total_row = combined[['total_allocation', 'state_component', 'iplc_component']].sum()
    total_row['party'] = 'EU Member States + European Union (total)'
    
    return combined, total_row

def aggregate_special_groups(df):
    ldc = df[df['is_ldc']][['total_allocation', 'state_component', 'iplc_component']].sum()
    sids = df[df['is_sids']][['total_allocation', 'state_component', 'iplc_component']].sum()
    
    return ldc, sids

def aggregate_by_income(df):
    agg = df.groupby('WB Income Group', dropna=False)[['total_allocation', 'state_component', 'iplc_component']].sum().reset_index()
    return agg[agg['total_allocation'] > 0]
