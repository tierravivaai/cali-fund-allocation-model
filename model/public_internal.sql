-- =========================================
-- Public vs internal views for Superset
-- =========================================

-- 1) Internal view: keep everything for audit/debug
CREATE OR REPLACE VIEW allocation_country_internal AS
SELECT
  *
FROM allocation_country;

-- 2) Public view: human labels + only the fields people need
-- NOTE: Quoted aliases preserve spaces and punctuation for Superset display.
CREATE OR REPLACE VIEW allocation_country_public AS
SELECT
  party AS "Party",

  -- Reference inputs
  cbd_scale_pct AS "CBD assessed contribution (% of core budget)",
  pct_adj       AS "CBD contribution used in allocation (after minimum threshold)",

  -- Optional: keep this visible only if you want a share column in charts
  (share_final * 100.0) AS "Final share of total Cali Fund (%)",

  -- Headline values in USD millions per year
  alloc_usd_m AS "Total annual allocation (USD million)",
  iplc_usd_m  AS "IPLC envelope within allocation (USD million)",
  state_usd_m AS "State envelope within allocation (USD million)",

  -- Grouping columns (if present in your base view)
  un_region        AS "UN region (UNSD M49)",
  un_subregion     AS "UN sub-region (UNSD M49)",
  un_intermediate  AS "UN intermediate region (UNSD M49)",
  dev_status       AS "Development status",
  is_eu27          AS "EU-27 member"
FROM allocation_country
ORDER BY party;
