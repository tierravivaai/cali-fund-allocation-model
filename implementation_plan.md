Below is a **droid-ready implementation plan** (clear enough to execute without back-and-forth) for a **DuckDB + SQL + Superset** parameterised allocation model. It assumes you’ll run it with **ChatGPT Max Code** inside the droid.

---

# Implementation Plan: Cali Fund Allocation Model (DuckDB + SQL + Superset)

## 0) Goal

Build a reproducible model that:

* ingests **CBD assessed contributions** + **UNSD M49 regions** (+ **EU membership** + **developed/developing flag**)
* computes **country allocations** under a parameterised formula
* outputs:

  * country table
  * region/subregion/intermediate tables
  * EU member list + EU total
  * developed vs developing tables
  * pooled global envelope by combining developed country allocations
* is visualised in **Superset** with **parameter sliders** that change assumptions live.

---

## 1) Inputs: required tables (canonical schemas)

### 1.1 `cbd_assessed_contributions.csv`

**Source:** COP decision annex table (e.g., COP16 decision table).
**Purpose:** provides the assessed contribution percentage used as the base "need and capacity signal".

**Required columns (exact names):**

* `party` (STRING) — CBD contracting Party name exactly as in the COP table
* `cbd_scale_pct` (DOUBLE) — “Scale with ceiling” percentage (e.g., 0.008 for 0.008%)
* `is_party` (BOOLEAN) — default TRUE; keep for future cases
* `source_decision` (STRING) — e.g., `"CBD/COP/DEC/16/28"`

**Notes**

* Keep the values as percent units like the COP table (e.g., 0.008 = 0.008%).
* Do **not** include “Total” rows.
* Keep any non-state Party entries if they exist, but mark `is_party=FALSE` (example: “European Union” line item).

---

### 1.2 `unsd_m49.csv`

**Source:** UNSD M49 mapping (your “useme” file).
**Purpose:** provides official UN regional groupings by Party name (or codes if available).

**Required columns (exact names):**

* `party` (STRING) — name matching `cbd_assessed_contributions.party` (or a code mapping, see below)
* `un_region` (STRING) — UNSD “Region Name”
* `un_subregion` (STRING) — UNSD “Sub-region Name”
* `un_intermediate` (STRING) — UNSD “Intermediate Region Name” (can be empty)
* `dev_status` (STRING) — must be one of: `developed`, `developing` (if absent, set NULL)

**Notes**

* Use names, not codes, for reporting.
* If you have ISO3/M49 codes, add them, but do not rely on them unless both datasets have them.

---

### 1.3 `eu27.csv`

**Purpose:** EU overlay table for a politically useful aggregation.

**Required columns:**

* `party` (STRING)
* `is_eu27` (BOOLEAN) — TRUE for EU-27 members

**Notes**

* Maintain as a small static file. Don’t derive it automatically.

---

### 1.4 Optional: `manual_name_map.csv`

**Purpose:** fix name mismatches (line breaks, accents).

**Columns:**

* `party_raw` (STRING) — as in CBD table
* `party_mapped` (STRING) — as in UNSD table

**Rule**

* Apply mapping before joins.
* Keep this small and explicit.

---

## 2) Variables / parameters (to be driven by Superset)

All parameters should be in a single “parameter CTE” so Superset can override them easily.

### Required parameters

* `fund_usd` (DOUBLE)

  * example values: 1e9, 5e9
  * slider range suggestion: 0.5e9 to 10e9
* `iplc_share` (DOUBLE)

  * default: 0.50
  * slider range: 0.50 to 0.80
* `smoothing_exponent` (DOUBLE)

  * default: 0.5 (square-root smoothing)
  * range: 0.33 to 1.0
  * interpretation: weight = (1 / pct_adjusted) ^ smoothing_exponent
* `pct_lower_bound` (DOUBLE)

  * default: 0.01 (meaning 0.01%)
  * range: 0.001 to 0.05
  * interpretation: pct_adjusted = max(cbd_scale_pct, pct_lower_bound)
* `cap_share` (DOUBLE)

  * default: 0.02 (2%)
  * range: 0.01 to 0.05
* `blend_baseline_share` (DOUBLE)

  * default: 0.00 (no baseline)
  * range: 0.00 to 0.50
  * interpretation: fraction of fund distributed as equal baseline
* `baseline_recipient` (STRING)

  * allowed: `all`, `developing`
  * default: `developing`

### Derived parameters (computed in SQL)

* `blend_inverse_share = 1 - blend_baseline_share`
* `cap_usd = cap_share * fund_usd`

---

## 3) Core model logic (SQL, deterministic)

### 3.1 Pre-processing join layer

1. Load tables into DuckDB.
2. Apply `manual_name_map` if provided.
3. Left join:

   * `cbd_assessed_contributions` → `unsd_m49`
   * `cbd_assessed_contributions` → `eu27`
4. Filter to CBD contracting Parties:

   * keep rows where `is_party = TRUE`
   * exclude obvious non-Parties (if any)

**Output view:** `v_party_base`

Columns:

* party
* cbd_scale_pct
* un_region, un_subregion, un_intermediate
* dev_status
* is_eu27

---

### 3.2 Weight calculation

Define:

* `pct_adj = greatest(cbd_scale_pct, pct_lower_bound)`
* `weight = power(1.0 / pct_adj, smoothing_exponent)`

This yields:

* exponent = 1.0 → raw inverse
* exponent = 0.5 → square-root smoothing
* exponent = 0.33 → stronger smoothing

---

### 3.3 Normalise to shares

* `share_raw = weight / sum(weight over all parties)`

---

### 3.4 Optional baseline component (Option 2)

If `blend_baseline_share > 0`:

* Determine eligible baseline set:

  * if `baseline_recipient = 'developing'`: dev_status = 'developing'
  * else: all Parties
* `baseline_share_each = 1 / count(eligible baseline parties)`
* `share_blend = blend_inverse_share * share_raw + blend_baseline_share * baseline_share_each (if eligible else 0)`

Else:

* `share_blend = share_raw`

---

### 3.5 Cap (apply after smoothing and blending)

Apply a maximum share per Party:

* `share_capped_pre = least(share_blend, cap_share)`
* Renormalise:

  * `share_final = share_capped_pre / sum(share_capped_pre)`

This is the “cap with proportional redistribution”.

---

### 3.6 Convert to money + IPLC split

* `alloc_usd = share_final * fund_usd`
* `iplc_usd = alloc_usd * iplc_share`
* `state_usd = alloc_usd * (1 - iplc_share)`

Also produce USD millions for readability:

* `alloc_usd_m = alloc_usd / 1e6` etc.

---

## 4) Output views/tables (what Superset will chart)

Create these as DuckDB views (or materialised tables if performance requires).

### 4.1 `v_alloc_country`

One row per Party:

* party, un_region, un_subregion, un_intermediate
* dev_status, is_eu27
* cbd_scale_pct, pct_adj
* share_final
* alloc_usd_m, iplc_usd_m, state_usd_m

Sort order: alphabetical by party (for table views).

---

### 4.2 `v_alloc_region`

Group by `un_region`:

* parties_count
* alloc_usd_m_total
* iplc_usd_m_total
* state_usd_m_total

---

### 4.3 `v_alloc_subregion`

Group by `un_region, un_subregion`

---

### 4.4 `v_alloc_intermediate`

Group by `un_region, un_subregion, un_intermediate`
(allow NULL intermediate; group as “(none)” in Superset)

---

### 4.5 `v_alloc_eu`

EU member list + EU totals:

* party, alloc_usd_m, iplc_usd_m, state_usd_m for is_eu27=TRUE
* plus a total row (or separate total view `v_alloc_eu_total`)

---

### 4.6 `v_alloc_devstatus`

Two grouped totals:

* developed total
* developing total

And optional per-country lists:

* `v_alloc_developed_country`
* `v_alloc_developing_country`

---

### 4.7 Optional: `v_alloc_pooling`

If you want voluntary pooling scenarios:

* parameter: `pooling_rate` (0–1)
* compute pooled envelope from:

  * developed countries, or EU only
* output:

  * `pooled_usd_m = pooling_rate * sum(alloc_usd where dev_status='developed') / 1e6`

---

## 5) Superset implementation (dashboard + filters)

### 5.1 Connect Superset to DuckDB

Recommended: DuckDB as a file DB (read-only), or DuckDB through a service.

* Put the DuckDB file in a stable location.
* Ensure Superset has read permissions.

### 5.2 Expose parameters

Superset doesn’t “inject variables into views” automatically; easiest patterns:

**Pattern A (recommended): use templated SQL in Superset datasets**

* Create a Superset Dataset using a SQL query that contains Jinja parameters:

  * `{{ fund_usd }}`, `{{ smoothing_exponent }}`, etc.
* Add dashboard filter controls mapped to those parameters.

**Pattern B: create a `params` table and update it**

* Store one row in `params`
* Change it via SQL Lab (less slider-friendly unless you build a small update mechanism)

Use Pattern A unless you have a custom control layer.

### 5.3 Dashboard components

* Table: country allocations (alphabetical) + search
* Bar chart: top 20 recipients
* Region totals table
* EU member table + EU total
* Developed vs developing totals
* KPI cards:

  * total IPLC envelope
  * total state envelope
  * pooled envelope (if enabled)

---

## 6) Validation tests (must-have)

Create a `tests/` script (Python) that checks:

* Shares sum to 1.0 (within tolerance)
* Total allocation equals fund size
* IPLC + State equals total
* Cap respected (no Party share > cap_share + tolerance)
* No missing UNSD regions for Parties (report list)
* Reproducibility across runs

---

## 7) Droid execution steps (what the droid should do)

1. Create repo structure
2. Add `data/` CSVs exactly as per schema above
3. Create `model/allocation.sql`:

   * contains parameter CTE
   * defines `v_alloc_*` views
4. Create `run_duckdb.py` to:

   * load CSVs into DuckDB
   * create views
   * optionally export parquet/csv outputs
5. Create `tests/test_reconciliation.py`
6. Create `superset/dashboard_spec.md`:

   * dataset SQL template
   * filter definitions + ranges
   * chart list and configuration notes
7. Produce a **single command** to build:

   * `python run_duckdb.py --db cali_fund.duckdb`

---

## 8) Defaults (start here)

Set defaults to:

* fund_usd = 1e9
* iplc_share = 0.5
* smoothing_exponent = 0.5
* pct_lower_bound = 0.01
* cap_share = 0.02
* blend_baseline_share = 0.2 (for the “Brazil-safe” option)
* baseline_recipient = developing

---

## Additional notes

Superset filter suggestions (map to Jinja vars)

Create dashboard filters that set these Jinja variables:

fund_usd (slider): 500000000 → 10000000000

iplc_share (slider): 0.5 → 0.8

smoothing_exponent (slider): 0.33 → 1.0

pct_lower_bound (slider): 0.001 → 0.05

cap_share (slider): 0.01 → 0.05

blend_baseline_share (slider): 0.0 → 0.5

baseline_recipient (dropdown): 'developing', 'all'

Important: in Jinja, strings should include quotes. So the dropdown should set values like:

'developing'

'all'


## 9) What to deliver at the end (acceptance criteria)

* DuckDB database file: `cali_fund.duckdb`
* Views exist:

  * `v_alloc_country`, `v_alloc_region`, `v_alloc_subregion`, `v_alloc_intermediate`,
    `v_alloc_eu`, `v_alloc_devstatus`
* A Superset dashboard can:

  * change fund size, exponent, lower bound, cap, blend weight, and IPLC share
  * see tables/charts update accordingly
* Tests pass

---
