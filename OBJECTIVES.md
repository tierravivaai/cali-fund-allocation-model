This document is authoritative over code comments and dashboards

# Objectives Brief

**Cali Fund Allocation Model (DuckDB · SQL · Streamlit / Superset)**
*(For review and finalisation)*

## 1. Purpose

Develop a **parameterised, transparent allocation model** for the Cali Fund that enables Parties to explore **equity-based allocation outcomes** interactively.

The model is designed to **support negotiation, testing of assumptions, and consensus-building**, not to prescribe a single fixed allocation formula.

Trade-offs must be explicit, auditable, and adjustable through clearly defined parameters.

---

## 2. Core Design Principles

### 2.1 Sovereign Equality

* All **CBD Contracting Parties**, including States and the European Union, are treated as sovereign equals under the Convention.
* No allocation is based on biodiversity richness, species counts, or ecological metrics.

### 2.2 Equity Logic

* Allocation is grounded in **ability-to-pay logic**, using the CBD assessed contribution scale as the sole input signal.
* The assessed contribution scale is **inverted** to reflect relative need.

### 2.3 Moderation of Extremes

* Raw inversion of assessed contributions produces extreme outcomes at the lower end of the scale.
* The model must moderate these extremes using:

  * smoothing (exponent-based),
  * a lower bound on contribution values,
  * a hard cap on maximum per-Party shares.
* These mechanisms are technical safeguards to ensure plausibility and political workability.

### 2.4 Transparency

* Every step of the calculation must be visible and auditable.
* Internal technical variables may be retained for verification, but **public outputs must be human-readable**.

---

## 3. Indigenous Peoples and Local Communities (IPLCs)

* The model must explicitly show that **at least 50% of all allocations are earmarked for Indigenous Peoples and Local Communities**.
* IPLC allocations must be:

  * shown as part of each Party’s total allocation (not additional),
  * visible at Party and aggregated levels.
* The model does **not** prescribe delivery mechanisms; it only presents indicative envelopes consistent with agreed principles.

---

## 4. Political Practicality

### 4.1 Middle-Income Developing Countries

* The model must avoid outcomes where **high-biodiversity, middle-income developing countries** receive implausibly small allocations.
* This is addressed through:

  * lower-bound protection,
  * optional baseline blending,
  * adjustable parameters rather than hard-coded outcomes.

---

## 5. Regional Aggregation Rules

* All regional aggregation must use **official UNSD M49 classifications**:

  * Region,
  * Sub-region,
  * Intermediate region.
* These groupings are used **solely for reporting and visualisation** and do not affect allocation calculations.

---

## 6. European Union Treatment (Clarified and Final)

* The **European Union is a Contracting Party to the Convention**, alongside its individual Member States.

* The allocation model therefore treats:

  * each EU Member State, and
  * the European Union (represented in practice by the European Commission),
    as **separate Parties**, consistent with CBD practice and budget contributions.

* For reporting and analytical purposes, the model must support aggregation that:

  * combines EU Member States **and**
  * includes the European Union as a Party
    to show a consolidated **EU-27 + European Union** total.

* This aggregation is **explicitly labelled and explained** to avoid any implication of double counting and does not override Party-level allocations.

---

## 7. Parameterisation Requirements

The model must expose the following parameters so they can be adjusted interactively:

* Total fund size (USD per year),
* IPLC earmark share (default ≥ 50%),
* Smoothing exponent,
* Lower bound on assessed contribution percentages,
* Maximum cap on per-Party shares,
* Optional baseline allocation share,
* Baseline eligibility (all Parties vs least developed countries (LDC) Parties).

All parameters must have **sensible defaults** and **clearly defined safe ranges**.

---

## 8. Outputs

### 8.1 Party-Level Outputs

* Total annual allocation (USD millions),
* IPLC envelope (USD millions),
* State envelope (USD millions),
* Associated UNSD regions,
* Development status,
* EU Member State flag (where applicable),
* European Union Party row (where applicable).

### 8.2 Aggregated Outputs

* UNSD region totals,
* Sub-region totals,
* Intermediate region totals,
* EU Member States + European Union total,
* Developed vs least developed countries (LDC) Party totals.

---

## 9. Visualisation and Iteration Tools

* The primary objective is **rapid iteration and exploration** of parameter settings.
* **Streamlit** will be used as the primary interactive interface for:

  * rapid prototyping,
  * parameter sliders,
  * immediate visual feedback during model development and review.
* **Superset** may be used subsequently for more formal dashboards once assumptions stabilise.

All visual outputs must be intelligible to **non-technical delegates**.

---

## 10. Non-Goals (Explicit)

The model must **not**:

* rank Parties by biodiversity,
* allocate based on scientific output or data provision,
* prescribe political decisions,
* hard-code a single “correct” allocation formula.

---

## 11. Success Criteria

The model is successful if:

* parameters can be adjusted live without breaking totals,
* allocations remain intelligible and defensible,
* extreme outcomes are visibly moderated,
* IPLC allocations are explicit and unavoidable,
* the model can be used credibly in a multilateral negotiation and review context.

---