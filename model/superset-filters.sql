-- Superset Dataset SQL (Jinja-enabled)
-- This returns the country-level allocation table.
-- Use dashboard filters to set the Jinja parameters.

WITH
params AS (
  SELECT
    CAST({{ fund_usd | default(1000000000) }} AS DOUBLE)      AS fund_usd,
    CAST({{ iplc_share | default(0.5) }} AS DOUBLE)           AS iplc_share,
    CAST({{ smoothing_exponent | default(0.5) }} AS DOUBLE)   AS smoothing_exponent,
    CAST({{ pct_lower_bound | default(0.01) }} AS DOUBLE)     AS pct_lower_bound,
    CAST({{ cap_share | default(0.02) }} AS DOUBLE)           AS cap_share,
    CAST({{ blend_baseline_share | default(0.2) }} AS DOUBLE) AS blend_baseline_share,
    CAST({{ baseline_recipient | default("'developing'") }} AS VARCHAR) AS baseline_recipient
),
params2 AS (
  SELECT *, (1.0 - blend_baseline_share) AS blend_inverse_share
  FROM params
),

base_contrib AS (
  SELECT
    COALESCE(m.party_mapped, c.party) AS party,
    c.party                           AS party_raw,
    c.cbd_scale_pct,
    c.is_party,
    c.source_decision
  FROM cbd_assessed_contributions c
  LEFT JOIN manual_name_map m
    ON c.party = m.party_raw
),

party_base AS (
  SELECT
    b.party,
    b.party_raw,
    b.cbd_scale_pct,
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

weights AS (
  SELECT
    p.*,
    GREATEST(p.cbd_scale_pct, (SELECT pct_lower_bound FROM params2)) AS pct_adj,
    POW(
      1.0 / GREATEST(p.cbd_scale_pct, (SELECT pct_lower_bound FROM params2)),
      (SELECT smoothing_exponent FROM params2)
    ) AS weight
  FROM party_base p
),

shares_raw AS (
  SELECT
    w.*,
    weight / SUM(weight) OVER () AS share_raw
  FROM weights w
),

baseline_set AS (
  SELECT
    s.*,
    CASE
      WHEN (SELECT baseline_recipient FROM params2) = 'developing'
        THEN CASE WHEN LOWER(COALESCE(dev_status,'')) = 'developing' THEN 1 ELSE 0 END
      ELSE 1
    END AS baseline_eligible
  FROM shares_raw s
),

baseline_stats AS (
  SELECT SUM(baseline_eligible) AS n_baseline
  FROM baseline_set
),

shares_blended AS (
  SELECT
    b.*,
    CASE
      WHEN baseline_eligible = 1 THEN 1.0 / NULLIF((SELECT n_baseline FROM baseline_stats), 0)
      ELSE 0.0
    END AS baseline_share,
    (SELECT blend_inverse_share FROM params2) * share_raw
      + (SELECT blend_baseline_share FROM params2) * CASE
          WHEN baseline_eligible = 1 THEN 1.0 / NULLIF((SELECT n_baseline FROM baseline_stats), 0)
          ELSE 0.0
        END AS share_blend
  FROM baseline_set b
),

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
)

SELECT
  party,
  party_raw,
  un_region,
  un_subregion,
  un_intermediate,
  dev_status,
  is_eu27,

  cbd_scale_pct,
  pct_adj,

  share_final,

  share_final * (SELECT fund_usd FROM params2) AS alloc_usd,
  share_final * (SELECT fund_usd FROM params2) * (SELECT iplc_share FROM params2) AS iplc_usd,
  share_final * (SELECT fund_usd FROM params2) * (1.0 - (SELECT iplc_share FROM params2)) AS state_usd,

  (share_final * (SELECT fund_usd FROM params2)) / 1e6 AS alloc_usd_m,
  (share_final * (SELECT fund_usd FROM params2) * (SELECT iplc_share FROM params2)) / 1e6 AS iplc_usd_m,
  (share_final * (SELECT fund_usd FROM params2) * (1.0 - (SELECT iplc_share FROM params2))) / 1e6 AS state_usd_m

FROM shares_final
ORDER BY party;
