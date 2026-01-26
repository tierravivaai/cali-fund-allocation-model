import duckdb
import pandas as pd
import os

def load_data(con):
    # Base paths
    base_path = "data-raw"
    
    # 1. Load UN Scale of Assessment
    con.execute(f"CREATE TABLE un_scale AS SELECT * FROM read_csv_auto('{base_path}/UNGA_scale_of_assessment.csv')")
    
    # 2. Load UNSD Regions
    con.execute(f"CREATE TABLE unsd_regions AS SELECT * FROM read_csv_auto('{base_path}/unsd_region_useme.csv')")
    
    # 3. Load World Bank Income Classes
    con.execute(f"CREATE TABLE wb_income AS SELECT * FROM read_csv_auto('{base_path}/world_bank_income_class.csv')")
    
    # 4. Load EU27 Member States
    con.execute(f"CREATE TABLE eu27 AS SELECT * FROM read_csv_auto('{base_path}/eu27.csv')")
    
    # 5. Load Manual Name Map
    con.execute(f"CREATE TABLE name_map AS SELECT * FROM read_csv_auto('{base_path}/manual_name_map.csv')")

def get_base_data(con):
    # Combine and clean data
    sql = """
    WITH scale_2027 AS (
        SELECT 
            "Member State" as party_name, 
            CASE 
                WHEN "2027" = '-' OR "2027" = 'NA' THEN 0.0 
                ELSE CAST("2027" AS DOUBLE) 
            END as un_share
        FROM un_scale
    ),
    mapped_scale AS (
        SELECT 
            COALESCE(m.party_mapped, s.party_name) as party,
            s.un_share
        FROM scale_2027 s
        LEFT JOIN name_map m ON s.party_name = m.party_raw
    ),
    joined AS (
        SELECT 
            s.party,
            s.un_share,
            r."Region Name" as region,
            r."Sub-region Name" as sub_region,
            r."Least Developed Countries (LDC)" = 'LDC' as is_ldc,
            r."Small Island Developing States (SIDS)" = 'SIDS' as is_sids,
            w."Income group" as income_group,
            e.is_eu27 IS NOT NULL as is_eu_ms
        FROM mapped_scale s
        LEFT JOIN unsd_regions r ON s.party = r."Country or Area"
        LEFT JOIN wb_income w ON s.party = w.Economy
        LEFT JOIN eu27 e ON s.party = e.party
    )
    SELECT * FROM joined
    """
    # Ensure EU Party entry exists if not already there
    df = con.execute(sql).df()
    if 'European Union' not in df['party'].values:
        eu_entry = pd.DataFrame([{
            'party': 'European Union',
            'un_share': 0.0,
            'region': 'Europe',
            'sub_region': 'Western Europe',
            'is_ldc': False,
            'is_sids': False,
            'income_group': 'High income',
            'is_eu_ms': False
        }])
        df = pd.concat([df, eu_entry], ignore_index=True)
    
    return df
