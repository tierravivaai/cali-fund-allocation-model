-- model/allocation.sql
-- Cali Fund Allocation Model (DuckDB)
-- Parameterised with Jinja variables so the same SQL can be used in Superset.
--
-- Required input tables (already loaded into DuckDB):
--   cbd_assessed_contributions(party, cbd_scale_pct, is_party, is_state, source_decision)
--   unsd_m49(party, un_region, un_subregion, un_intermediate, dev_status)
--   eu27(party, is_eu27)
-- Optional:
--   manual_name_map(party_raw, party_mapped)

-- =========================
-- 0) PARAMETERS (Jinja)
-- =========================
-- In DuckDB, you can run this file as-is by replacing Jinja placeholders yourself,
-- or via Superset (Jinja supported), or via a Python runner that renders Jinja then executes.

CREATE OR REPLACE VIEW allocation_country AS
WITH
params AS (
  SELECT
    CAST({{ fund_usd | default(1000000000) }} AS DOUBLE)      AS fund_usd,               -- e.g. 1e9
    CAST({{ iplc_share | default(0.5) }} AS DOUBLE)           AS iplc_share,             -- 0.50
    CAST({{ smoothing_exponent | default(0.5) }} AS DOUBLE)   AS smoothing_exponent,     -- 0.5 = sqrt smoothing
    CAST({{ pct_lower_bound | default(0.01) }} AS DOUBLE)     AS pct_lower_bound,        -- in "percent units" like COP table
    CAST({{ cap_share | default(0.02) }} AS DOUBLE)           AS cap_share,              -- 0.02 = 2%
    CAST({{ blend_baseline_share | default(0.2) }} AS DOUBLE) AS blend_baseline_share,   -- 0.20 baseline
    CAST({{ baseline_recipient | default("'developing'") }} AS VARCHAR) AS baseline_recipient
),
params2 AS (
  SELECT
    *,
    (1.0 - blend_baseline_share) AS blend_inverse_share
  FROM params
),

-- =========================
-- 1) NAME MAPPING (optional)
-- =========================
base_contrib AS (
  SELECT
    COALESCE(m.party_mapped, c.party) AS party,
    c.party                           AS party_raw,
    c.cbd_scale_pct,
    c.is_party,
    c.is_state,
    c.source_decision
  FROM cbd_assessed_contributions c
  LEFT JOIN manual_name_map m
    ON c.party = m.party_raw
),

-- =========================
-- 2) PARTY BASE (join UNSD + EU)
-- =========================
party_base AS (
  SELECT
    b.party,
    b.party_raw,
    b.cbd_scale_pct,
    b.is_state,
    u.un_region,
    u.un_subregion,
    u.un_intermediate,
    u.dev_status,
    COALESCE(e.is_eu27, FALSE) AS is_eu27
  FROM base_contrib b
  LEFT JOIN unsd_m49 u ON b.party = u.party
  LEFT JOIN eu27 e     ON b.party = e.party
  WHERE b.is_party = TRUE
),

-- =========================
-- 3) WEIGHTS (smoothed inverse with lower bound)
-- =========================
weights AS (
  SELECT
    p.*,
    -- lower bound prevents micro-contributors from dominating
    GREATEST(p.cbd_scale_pct, (SELECT pct_lower_bound FROM params2)) AS pct_adj,

    -- weight = (1/pct_adj) ^ exponent
    POW(1.0 / GREATEST(p.cbd_scale_pct, (SELECT pct_lower_bound FROM params2)),
        (SELECT smoothing_exponent FROM params2)) AS weight
  FROM party_base p
),

-- =========================
-- 4) NORMALISE TO SHARES
-- =========================
shares_raw AS (
  SELECT
    w.*,
    weight / SUM(weight) OVER () AS share_raw
  FROM weights w
),

-- =========================
-- 5) OPTIONAL BASELINE BLEND (Option 2)
-- =========================
baseline_set AS (
  SELECT
    s.*,
    CASE
      WHEN (SELECT baseline_recipient FROM params2) = 'developing'
        THEN CASE WHEN LOWER(COALESCE(CAST(dev_status AS VARCHAR), '')) = 'developing' THEN 1 ELSE 0 END
      ELSE 1
    END AS baseline_eligible
  FROM shares_raw s
),
baseline_stats AS (
  SELECT
    SUM(baseline_eligible) AS n_baseline
  FROM baseline_set
),
shares_blended AS (
  SELECT
    b.*,
    -- equal baseline share among eligible parties
    CASE
      WHEN baseline_eligible = 1 THEN 1.0 / NULLIF((SELECT n_baseline FROM baseline_stats), 0)
      ELSE 0.0
    END AS baseline_share,

    -- blend (inverse + baseline)
    (SELECT blend_inverse_share FROM params2) * share_raw
      + (SELECT blend_baseline_share FROM params2) * CASE
          WHEN baseline_eligible = 1 THEN 1.0 / NULLIF((SELECT n_baseline FROM baseline_stats), 0)
          ELSE 0.0
        END AS share_blend
  FROM baseline_set b
),

-- =========================
-- 6) CAP (apply to blended shares, then renormalise)
-- =========================
shares_capped_pre AS (
  SELECT
    sb.*,
    LEAST(share_blend, (SELECT cap_share FROM params2)) AS share_capped_pre
  FROM shares_blended sb
),
shares_final AS (
  SELECT
    scp.*,
    share_capped_pre / SUM(share_capped_pre) OVER () AS share_final
  FROM shares_capped_pre scp
),

-- =========================
-- 7) MONEY + IPLC SPLIT
-- =========================
alloc_country AS (
  SELECT
    party,
    party_raw,
    un_region,
    un_subregion,
    un_intermediate,
    dev_status,
    is_eu27,
    is_state,

    cbd_scale_pct,
    pct_adj,

    share_final,

    -- USD
    share_final * (SELECT fund_usd FROM params2) AS alloc_usd,
    share_final * (SELECT fund_usd FROM params2) * (SELECT iplc_share FROM params2) AS iplc_usd,
    share_final * (SELECT fund_usd FROM params2) * (1.0 - (SELECT iplc_share FROM params2)) AS state_usd,

    -- USD millions
    (share_final * (SELECT fund_usd FROM params2)) / 1e6 AS alloc_usd_m,
    (share_final * (SELECT fund_usd FROM params2) * (SELECT iplc_share FROM params2)) / 1e6 AS iplc_usd_m,
    (share_final * (SELECT fund_usd FROM params2) * (1.0 - (SELECT iplc_share FROM params2))) / 1e6 AS state_usd_m
  FROM shares_final
)

-- =========================
-- 8) FINAL SELECTS
-- =========================

-- Country-level output (for Superset dataset)
SELECT *
FROM alloc_country
ORDER BY party;

CREATE OR REPLACE VIEW un_region AS
SELECT
  un_region,
  COUNT(*) AS parties_count,
  SUM(alloc_usd_m) AS alloc_usd_m_total,
  SUM(iplc_usd_m) AS iplc_usd_m_total,
  SUM(state_usd_m) AS state_usd_m_total
FROM allocation_country
GROUP BY un_region
ORDER BY un_region;

CREATE OR REPLACE VIEW un_subregion AS
SELECT
  un_region,
  un_subregion,
  COUNT(*) AS parties_count,
  SUM(alloc_usd_m) AS alloc_usd_m_total,
  SUM(iplc_usd_m) AS iplc_usd_m_total,
  SUM(state_usd_m) AS state_usd_m_total
FROM allocation_country
GROUP BY un_region, un_subregion
ORDER BY un_region, un_subregion;

CREATE OR REPLACE VIEW allocation_un_intermediate_region AS
SELECT
  un_region,
  un_subregion,
  COALESCE(CAST(un_intermediate AS VARCHAR), '(none)') AS un_intermediate,
  COUNT(*) AS parties_count,
  SUM(alloc_usd_m) AS alloc_usd_m_total,
  SUM(iplc_usd_m) AS iplc_usd_m_total,
  SUM(state_usd_m) AS state_usd_m_total
FROM allocation_country
GROUP BY un_region, un_subregion, COALESCE(CAST(un_intermediate AS VARCHAR), '(none)')
ORDER BY un_region, un_subregion, COALESCE(CAST(un_intermediate AS VARCHAR), '(none)');

CREATE OR REPLACE VIEW allocation_eu AS
SELECT *
FROM allocation_country
WHERE is_eu27 = TRUE
ORDER BY party;

CREATE OR REPLACE VIEW allocation_eu_total AS
SELECT
  SUM(alloc_usd_m) AS alloc_usd_m_total,
  SUM(iplc_usd_m) AS iplc_usd_m_total,
  SUM(state_usd_m) AS state_usd_m_total
FROM allocation_country
WHERE is_eu27 = TRUE;

CREATE OR REPLACE VIEW allocation_devstatus AS
SELECT
  COALESCE(CAST(dev_status AS VARCHAR), 'unknown') AS dev_status,
  COUNT(*) AS parties_count,
  SUM(alloc_usd_m) AS alloc_usd_m_total,
  SUM(iplc_usd_m) AS iplc_usd_m_total,
  SUM(state_usd_m) AS state_usd_m_total
FROM allocation_country
GROUP BY COALESCE(CAST(dev_status AS VARCHAR), 'unknown')
ORDER BY COALESCE(CAST(dev_status AS VARCHAR), 'unknown');

