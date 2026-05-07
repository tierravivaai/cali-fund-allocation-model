Priority instruction

Follow the existing repo logic as the source of truth. Do not redesign the model. Build a separate `sensitivity.py` app in the same repo, add sensitivity metrics and reporting helpers, and generate both rigorous diagnostics and professionally written markdown reports for human review. Prioritise correctness, reproducibility, and readable outputs over UI polish.

Below is a single consolidated instruction set you can give to the droid.

---

# Droid Instructions: Build a Separate Sensitivity Testing App and Reporting Layer for the Cali Allocation Model v2 Repo

## Goal

Build a **separate Streamlit sensitivity testing app** inside the **same repository** as the main Cali Allocation Model v2 app.

The sensitivity app must rigorously test the **Inverted UN Scale of Assessment Formula (IUSAF)** model with **TSAC** and **SOSAC**, including scenarios at **US$50 million, US$200 million, US$500 million, and US$1 billion**.

The app must also generate **professionally written human-readable reports** that explain the results in a disciplined, critical, non-polemical style suitable for scrutiny by sceptical reviewers.

This is not a general dashboard. It is a **robustness-testing and reporting tool**.

---

## Repository decision

Do **not** create a separate repo.

Implement this work in the **same repo** as the main app, so both the negotiation app and the sensitivity app use the **same core calculation logic**, data, eligibility rules, and configuration. This is important to avoid logic drift and to preserve credibility.

---

## Core design principle

The sensitivity app must use the **existing model logic as the source of truth**.

Do not reimplement core allocation logic unless absolutely necessary. Reuse existing calculator functions and configs wherever possible.

The sensitivity app should sit alongside the main app as a second Streamlit entry point.

---

## Expected files

Create or update the following files:

* `sensitivity.py` — separate Streamlit app for sensitivity testing
* `logic/sensitivity_metrics.py` — helper functions for metrics and diagnostics
* `logic/sensitivity_scenarios.py` — scenario libraries and sweep generation
* `logic/reporting.py` — narrative report generation functions
* optionally `templates/` if templating is helpful, but this is not required
* update `README.md` to explain how to run both apps

Possible template files if needed:

* `templates/scenario_brief.md.j2`
* `templates/sweep_summary.md.j2`
* `templates/comparative_report.md.j2`
* `templates/technical_annex.md.j2`

If templating adds complexity, use plain Python string builders instead.

---

## Existing repo context to respect

Use the current repository structure and treat existing logic as authoritative, especially:

* `app.py`
* `logic/calculator.py`
* related group aggregation and warning functions
* existing config such as UN scale band settings

Respect existing logic for:

* eligibility
* equality mode
* raw inversion vs band inversion
* TSAC and SOSAC blending
* no-SIDS fallback
* floor and ceiling handling
* IPLC split

The sensitivity app must test the model that actually exists, not an abstract version of it.

---

## Functional objective

The sensitivity app must answer the following kinds of questions:

1. Is the model mathematically sound across tested scenarios?
2. Are the outcomes stable when assumptions are varied?
3. At what point do TSAC and SOSAC materially change the distribution?
4. At what point do floor and ceiling constraints materially shape the results?
5. How much do outputs change under plausible alternative assumptions?
6. Which changes are modest, and which amount to structural breaks?
7. Can the outputs be explained clearly to a critical human reader?

---

# App architecture

## Streamlit entry points

The repo should contain:

* `app.py` — existing main negotiation/policy app
* `sensitivity.py` — new dedicated sensitivity and reporting app

The two apps must share the same underlying calculation logic.

---

## Suggested internal structure

### `sensitivity.py`

Responsible for:

* loading inputs
* rendering UI
* selecting baselines and scenarios
* running sweeps
* calling metrics functions
* calling report generation functions
* exporting CSV and markdown outputs

### `logic/sensitivity_scenarios.py`

Responsible for:

* named scenarios
* one-way sweep definitions
* two-way grid sweep definitions
* baseline scenario definition
* scenario comparison helpers

### `logic/sensitivity_metrics.py`

Responsible for:

* invariant tests
* concentration metrics
* rank stability metrics
* group summaries
* threshold tests
* structural break rules
* country delta calculations

### `logic/reporting.py`

Responsible for:

* converting metrics into disciplined prose
* generating scenario brief text
* generating sweep summary text
* generating comparative report text
* generating technical annex text
* narrative classification helpers

---

# Sensitivity app UI structure

Use four main tabs:

## Tab 1. Parameter Sweep

For:

* single scenario runs
* one-way sweeps
* two-way grid sweeps
* scenario library runs

Outputs:

* tables
* clear charts
* downloadable CSVs
* short interpretation text

## Tab 2. Robustness Diagnostics

For:

* invariant tests
* edge-case tests
* normalization checks
* no-negative checks
* fallback checks
* structural break checks

Outputs:

* pass/fail status
* diagnostics table
* written interpretation

## Tab 3. Thresholds and Tipping Points

For:

* identifying where scenarios begin to diverge materially
* showing when TSAC/SOSAC start to override IUSAF logic
* showing when floor/ceiling begin to shape results
* showing when rank stability drops materially

Outputs:

* threshold charts
* summary tables
* narrative text

## Tab 4. Attack Surface Report

For:

* translating results into plain analytical prose
* showing likely criticisms and the empirical response
* identifying gainers, losers, and structural effects
* generating downloadable markdown reports

Outputs:

* readable prose
* markdown download buttons
* structured comparison summaries

---

# Parameter coverage

The app must support the following test ranges.

## Fund sizes

Use fixed scenario anchors:

* 50,000,000
* 200,000,000
* 500,000,000
* 1,000,000,000

## UN inversion modes

* raw inversion
* band inversion

## Eligibility

* exclude high-income except SIDS = True
* exclude high-income except SIDS = False

## TSAC range

Sweep from:

* 0% to 15%
  Prefer step size:
* 1 percentage point

## SOSAC range

Sweep from:

* 0% to 10%
  Prefer step size:
* 1 percentage point

## IPLC share

Test:

* 50%
* 60%
* 70%
* 80%

## Floor

Test:

* off
* 0.05%
* 0.10%
* 0.25%
* dynamic max-safe values where relevant

## Ceiling

Test:

* off
* 1%
* 2%
* 5%

---

# Baselines and benchmark scenarios

The app must compare results against consistent reference points.

## Default baseline

Use:

* fund size = 1bn
* band inversion
* exclude high income except SIDS = True
* TSAC = 5%
* SOSAC = 3%
* IPLC share = 50%
* floor off
* ceiling off

## Mandatory benchmarks

Always support comparison against:

* pure equality
* pure IUSAF
* balanced baseline

This gives three interpretable anchors:

* equality benchmark
* inverted UN benchmark
* compromise benchmark

---

# Required scenario library

Create a named scenario library with at least the following:

* `pure_equality`
* `pure_iusaf_raw`
* `pure_iusaf_band`
* `balanced_baseline`
* `balanced_5_3`
* `terrestrial_max`
* `ocean_max`
* `balanced_floor_005`
* `balanced_ceiling_1`
* `balanced_floor_005_ceiling_1`
* `exclude_hi_off_compare`
* `exclude_hi_on_compare`
* `raw_vs_band_compare`

Each scenario must be reproducible from explicit parameters.

---

# Integrity and invariant tests

These tests are mandatory.

## 1. Conservation of shares

For each scenario:

* sum of final eligible country shares must equal 1.0 within numerical tolerance

## 2. Conservation of money

For each scenario:

* total allocations must sum to total fund size within tolerance

## 3. Internal component consistency

For each country:

* state allocation + IPLC allocation must equal total allocation within tolerance

## 4. Non-negativity

All share and monetary values must be non-negative.

## 5. Equality mode correctness

When equality mode is active:

* all eligible countries receive equal shares
* TSAC and SOSAC should not distort equality mode outputs

## 6. Raw inversion correctness

Under raw inversion:

* countries with lower positive UN shares should not receive lower base inverted weights than countries with higher UN shares, unless later modified by stewardship components or constraints

## 7. Band inversion correctness

Under band inversion:

* all eligible countries with valid UN shares must be assigned to a valid configured band

## 8. No-SIDS fallback

If there are no eligible SIDS and SOSAC is positive:

* SOSAC must be reallocated back into IUSAF
* final shares must still normalize correctly

## 9. Floor feasibility

Floor logic must never break normalization.
If the floor is infeasible or highly binding, that must be surfaced clearly.

## 10. Ceiling feasibility

Ceiling logic must never break normalization.
If the ceiling materially compresses outcomes, that must be surfaced clearly.

## 11. Scale invariance of shares

For fixed parameter settings:

* fund size changes must change monetary values only
* share distribution should remain unchanged

---

# Sensitivity test design

## A. One-way sensitivity

Vary one parameter at a time from the baseline.

For each run, compute impact on:

* rank stability
* top 10 and top 20 shares
* group totals
* concentration
* equality distance
* gainers and losers

## B. Two-way sensitivity

Run grid sweeps for:

* TSAC × SOSAC
* floor × ceiling
* UN mode × TSAC
* UN mode × SOSAC
* exclude-high-income × TSAC

For each grid cell, compute key outcome metrics and warning thresholds.

## C. Four anchor fund scenarios

Run key sweeps at:

* 50m
* 200m
* 500m
* 1bn

Even where shares do not change, the app should still report how interpretive and political significance changes.

## D. Extreme-case tests

Include defensible stress scenarios such as:

* pure equality
* pure IUSAF
* maximum TSAC
* maximum SOSAC
* balanced
* balanced with floor
* balanced with ceiling
* balanced with both floor and ceiling
* raw inversion extreme
* band inversion extreme

## E. Structural-break testing

Identify when scenarios cease to be modest variations and become materially different distributions.

---

# Required metrics

Compute the following metrics for every scenario.

## Scenario identifiers

* `scenario_id`
* `fund_size`
* `un_scale_mode`
* `exclude_hi`
* `iplc_share`
* `tsac_beta`
* `sosac_gamma`
* `floor_pct`
* `ceiling_pct`

## Counts

* `n_eligible`
* `n_sids_eligible`
* `floor_binding_count`
* `ceiling_binding_count`

## Integrity

* `sum_final_share`
* `sum_total_allocation`
* `negative_count`

## Distribution

* `top10_share`
* `top20_share`
* `mean_alloc`
* `median_alloc`
* `p90_p10_ratio`
* `hhi`
* `gini`

## Robustness

* `pct_below_equality`
* `median_pct_of_equality`
* `spearman_vs_iusaf`
* `spearman_vs_equality`
* `top20_turnover_vs_iusaf`

## Group outcomes

* `ldc_total`
* `sids_total`
* totals by region
* totals by World Bank income group

## Narrative and warning flags

* `stewardship_warning_level`
* `outcome_warning_flag`
* `structural_break_flag`
* `dominance_flag`

---

# Structural break rules

Set `structural_break_flag = True` if any of the following hold:

* TSAC + SOSAC > 0.20
* Spearman rank correlation vs pure IUSAF < 0.95
* top-20 turnover vs pure IUSAF > 20%
* pct_below_equality > 60%
* median_pct_of_equality < 90%

These thresholds should be coded centrally and used consistently across metrics and reporting.

---

# Attack-surface analysis

The app must specifically test likely lines of criticism.

## 1. “TSAC/SOSAC defeat the base model”

Quantify:

* divergence from pure IUSAF
* rank changes
* magnitude of reallocation away from IUSAF baseline
* whether stewardship weights remain supplementary or become dominant

## 2. “Band inversion is arbitrary”

Compare:

* raw inversion vs band inversion
* country rank changes
* compression of extremes
* effect on concentration and outliers

## 3. “Floor and ceiling are doing the real work”

Quantify:

* number of countries bound by floor
* number bound by ceiling
* share of total allocation redistributed due to constraints
* rank changes caused by constraints alone

## 4. “Excluding high-income countries determines the result”

Compare:

* exclude-high-income on vs off
* pool composition changes
* effects on eligible developing countries
* effects on SIDS and LDCs

## 5. “SOSAC is a political subsidy rather than a modelled component”

Decompose:

* SIDS outcomes under pure IUSAF
* SIDS outcomes under SOSAC-only
* SIDS outcomes under balanced scenarios
* component contributions to SIDS totals

---

# Charts and visuals

Use only charts that have analytical value.

## Required visuals

* TSAC × SOSAC heatmap with selectable metric
* tornado chart for one-way sensitivity
* rank stability plot for selected countries or groups
* floor/ceiling binding chart
* threshold chart for warning regions

## Heatmap metrics to support

Prefer heatmaps for:

* Spearman rank correlation vs IUSAF
* percentage below equality benchmark
* SIDS share
* concentration or HHI
* top-20 turnover

## Avoid

* decorative charts
* redundant charts
* visuals with no explanatory value

---

# Reporting layer requirements

The app must generate professionally written narrative outputs for critical human readers.

This reporting layer is mandatory. The app must not stop at data tables and charts.

---

## Written outputs to generate

### 1. Scenario Brief

A concise markdown note for a selected scenario.

Purpose:

* explain a single scenario clearly
* suitable for a negotiator or analyst

### 2. Sweep Summary

A concise markdown note for a one-way or two-way sensitivity sweep.

Purpose:

* explain what the sweep shows
* identify strongest drivers and thresholds

### 3. Comparative Sensitivity Report

A fuller markdown report comparing:

* baseline
* equality benchmark
* pure IUSAF
* selected stress scenarios

Purpose:

* support scrutiny of overall model robustness

### 4. Technical Annex

A methods-focused markdown appendix documenting:

* formulas
* assumptions
* test ranges
* invariants
* thresholds
* edge-case handling

Purpose:

* answer methodological criticism directly

---

# Writing style requirements

The reporting must be written in a professional analytical style.

## Required tone

* measured
* precise
* restrained
* explicit about limitations
* explicit about uncertainty
* non-polemical
* non-advocacy

## Use phrasing such as

* “The results suggest…”
* “Within the tested range…”
* “The model remains broadly stable under…”
* “This parameter has a material effect on…”
* “This should be interpreted with caution because…”
* “At higher stewardship weights, the distribution begins to diverge from the pure IUSAF baseline…”

## Avoid phrasing such as

* “proves”
* “beyond doubt”
* “cannot be criticised”
* “opponents are wrong”
* “clearly fair in every respect”

The prose should sound like a serious analyst, not a campaigner.

---

# Narrative rule system

Implement helper functions in `logic/reporting.py` that convert metrics into consistent prose.

## Rank stability language

* `>= 0.98` → “very limited divergence from the pure IUSAF baseline”
* `0.95 to <0.98` → “modest divergence”
* `0.90 to <0.95` → “noticeable divergence”
* `< 0.90` → “material divergence”

## Stewardship influence language

* `TSAC + SOSAC <= 0.10` → “stewardship components play a limited supplementary role”
* `>0.10 and <=0.20` → “stewardship components make a visible but not dominant contribution”
* `>0.20` → “stewardship components materially shape the final distribution”

## Floor/ceiling influence language

* `<10%` of eligible countries bound → “constraints play a limited role”
* `10% to 30%` bound → “constraints have a visible equalising effect”
* `>30%` bound → “constraints materially shape the distribution”

## Equality distance language

* `pct_below_equality <= 40%` → “outcomes remain broadly consistent with a widely distributed allocation pattern”
* `>40% and <=60%` → “distribution becomes more selective”
* `>60%` → “distribution departs substantially from equality-style allocation”

These rules should be deterministic and reused across scenario briefs, sweep summaries, and comparative reports.

---

# Required report structures

## Scenario Brief

Must include:

* Title
* Purpose
* Scenario Definition
* Main Findings
* Distributional Effects
* Stability Relative to Baseline
* Interpretive Notes
* Limitations
* Bottom Line

## Sweep Summary

Must include:

* Title
* Purpose of Sweep
* Sweep Design
* Main Patterns
* Parameters with Largest Effect
* Thresholds / Tipping Points
* Caveats
* Bottom Line

## Comparative Sensitivity Report

Must include:

* Title
* Introduction
* Baseline Scenario
* Benchmarks for Comparison
* Test Design
* Main Results
* Group-Level Effects
* Robustness Assessment
* Structural Break Scenarios
* Conclusions

## Technical Annex

Must include:

* Data and Eligibility Rules
* Formula Specification
* Raw vs Band Inversion
* TSAC and SOSAC Treatment
* IPLC Split
* Floor and Ceiling Handling
* No-SIDS Fallback
* Integrity Tests
* Sensitivity Ranges
* Structural Break Criteria
* Exported Outputs

---

# In-app readable interpretation

Each main tab in the Streamlit app must end with a clearly labelled interpretation section containing 2 to 5 paragraphs of readable prose summarising the current result set.

This prose must:

* reflect actual computed metrics
* identify main patterns
* note important caveats
* distinguish modest from material change

The app must include download buttons for the corresponding markdown report.

---

# Exports

The app must provide downloads for:

## Written outputs

* Scenario Brief `.md`
* Sweep Summary `.md`
* Comparative Report `.md`
* Technical Annex `.md`

## Data outputs

* scenario metrics CSV
* country-level results CSV
* country-level deltas CSV
* group summary CSV

Each report should reference exported filenames where appropriate.

---

# Coding requirements

* Reuse existing calculator logic wherever possible
* Keep calculations separate from rendering
* Keep reporting separate from calculations
* Minimise changes to existing core calculator unless strictly necessary
* If changes to existing logic are required, keep them backward compatible
* Use caching where appropriate for scenario grids
* Keep plots clear and sparse
* Document assumptions in code comments
* Ensure outputs are reproducible from explicit parameter settings

---

# Validation requirements

Before considering the task complete, run checks for:

* full scenario library integrity
* TSAC × SOSAC grid across the full allowed range
* no crash when no eligible SIDS exist
* no crash when floor is off
* no crash when ceiling is off
* no crash when only one constraint is enabled
* no crash when equality mode is selected
* correct operation of markdown downloads
* correct operation of CSV downloads

---

# README update

Update the README to explain:

* the repo now contains two apps
* how to launch the main app
* how to launch the sensitivity app

Include at least:

```bash
streamlit run app.py
streamlit run sensitivity.py
```

Also briefly explain what the sensitivity app is for.

---

# Definition of done

The work is complete only when all of the following are true:

1. `streamlit run sensitivity.py` works
2. the sensitivity app reuses the same core model logic as the main app
3. invariant tests and sensitivity tests run in-app
4. the app can compare baseline, equality, and pure IUSAF
5. the app clearly identifies modest versus structural change
6. the app generates readable professional markdown reports
7. the app exports all required CSV and markdown outputs
8. the reporting language is measured and analytically credible
9. the output is suitable for scrutiny by a critical human reviewer

---

# Practical implementation priority

If time or complexity becomes an issue, prioritise in this order:

1. correct reuse of calculator logic
2. invariant tests
3. one-way and two-way sweeps
4. scenario library
5. written interpretation blocks in app
6. markdown report export
7. technical annex generation
8. polish and refactoring

Do not sacrifice analytical correctness for UI polish.

---

# Final instruction to droid

Build the sensitivity testing and reporting system as a serious analytical tool, not a decorative dashboard. The main purpose is to show how the model behaves under scrutiny, identify where it is stable, identify where it changes materially, and explain those results in clear professional prose.

---

If you want, I can also turn this into a shorter **SKILL.md-style version** with tighter formatting for direct paste into Factory.
