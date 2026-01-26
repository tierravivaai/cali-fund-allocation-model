# Objectives Brief (UN Scale — Minimal Controls)

**Cali Fund Allocation Model (UN Scale) — DuckDB · SQL · Streamlit**

## 1) Purpose

Provide a simple, transparent tool to illustrate how Cali Fund allocations would look if distribution were based on the **latest UN Scale of Assessments (general scale)**, inverted to reflect relative need. The tool supports negotiation by making the consequences of this choice visible without technical complexity.

## 2) Core Method

* Input: each Party’s **UN Scale of Assessments share (%)** for the year 2027 (to be labelled as 2025-2027).
* Allocation: compute each Party’s **inverted share** of the Cali Fund and allocate accordingly.
* No biodiversity indicators are used.
* No additional “engineering” steps (smoothing, lower bounds, blend weights) are exposed to users.

## 3) IPLCs

* The tool must show an **explicit IPLC earmark** (default 50%) within each Party’s allocation.
* IPLC allocation is treated as **part of** the Party allocation, not additional:

  * Total allocation = IPLC envelope + State envelope.

## 4) EU treatment

* The **European Union is a Party**, and EU Member States are also Parties.
* The tool must show:

  * EU Member States individually,
  * the European Union Party entry,
  * and a clearly labelled **“EU Member States + European Union (total)”** aggregation.
* This aggregation is for visibility; it does not override Party-level allocations.

## 5) Regions

* Aggregation must use **UNSD M49 region / sub-region / intermediate region names** for reporting only.

## 6) World Bank income classification

The model must include World Bank country income groups (e.g. low income, lower-middle income, upper-middle income, high income) as descriptive labels only.

Income classification must:

- be joined after allocation calculations,
- have no influence on allocation logic,
- be used solely for interpretation and grouping of results.

The application must provide a direct link to the official World Bank source file used for the classification.
The source file link is: https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups

Clarifying statement (to include in documentation/UI):

“World Bank income groups are shown for interpretative purposes only and do not affect allocation calculations.”

## 7) Outputs

* Party table (alphabetical): total allocation, IPLC envelope, State envelope (USD millions/year)
* UNSD region/subregion/intermediate totals (USD millions/year)
* EU block view (members + EU Party + total)
* Developed vs Least developed countries (LDC) totals (if dev_status available)

## 8) Non-goals

* Do not expose technical parameters to users.
* Do not claim this is the final decision of the COP; it is an illustrative calculator.

## 9) Success criteria

A non-technical user can:

* set the fund size,
* set the IPLC share,
* optionally view the raw inversion logic,
* and immediately understand the resulting allocations.

## 10) Resources

- UN Scale of Assessments document:  
  "data-raw/UNGA_scale_of_assessment.csv"
  - Note use the Member State column and the year 2027 which should be labelled as 2025-2027
- UNSD Regions = "/data-raw/unsd_region_useme.csv"
- UNSD name reconciliation map (if needed) = "data-raw/manual_name_map.csv"
- World Bank Income Classification = "/data-raw/world_bank_income_class.csv"
- EU27 Member States = "/data-raw/eu27.csv"
---

# Streamlit Controls (Minimal, Non-technical)

### Always visible (only two sliders)

1. **Annual Cali Fund size (USD)**

* Slider or number input
* Defaults: `1,000,000,000`
* Range suggestion: `100,000,000` to `10,000,000,000`
* Display format: billions (e.g. “$1.0bn”, “$5.0bn”)

2. **Share earmarked for Indigenous Peoples & Local Communities (%)**

* Slider
* Default: `50%`
* Range: `50%` to `80%` (or whatever you prefer)
* Tooltip: “This splits each Party’s allocation into an IPLC envelope and a State envelope. Together they equal the total.”

### One optional toggle (explanatory only)

3. **Show “raw inversion” (illustrative only)** *(toggle)*

* Default: OFF
* When ON:

  * show a short note: “Raw inversion shown for explanation. Results can be extreme.”
  * show an extra column or tab that displays the raw inverted shares side-by-side with the default view.

**Important:** Do not add any other sliders.

### Optional (safe) UI convenience

4. **Reset to default** button

* Sets fund size back to 1bn and IPLC share back to 50%, and turns OFF raw inversion.

5. **Validation checks**

* Add background checks for all calculations to ensure allocations sum to the fund size, and IPLC + State envelopes sum to total allocations.

---

# Recommended Streamlit Page Layout

* **Header:** title + one-sentence disclaimer (“illustrative only”)
* **Controls panel:** fund size + IPLC share + raw inversion toggle
* **Main tabs:**

  * **By Party (A–Z)** (searchable table)
  * **By UN Region** (totals)
  * **EU block** (EU MS + EU Party + total)
  * **Developed vs developing** (totals)

All money shown as: **USD millions per year**.

* **Disclaimer** At bottom of page or in footer:  

"This interactive tool is provided purely for illustrative and exploratory purposes. It has no status.
The allocations shown are indicative and are generated using an inverted [UN Scale of Assessments](https://digitallibrary.un.org/record/4071844?ln=en&utm_source=chatgpt.com&v=pdf#files) to support discussion."
