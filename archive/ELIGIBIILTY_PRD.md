## Droid implementation instructions

**Feature: Exclude High Income countries (Option A)**

### Objective

Add a toggle that **excludes High Income countries from receiving allocations**, while keeping them visible in outputs with **zero allocation**, and **reallocates the full fund to the remaining eligible countries**.

---

### UI (Streamlit)

Add a single checkbox:

> **Exclude High Income countries from receiving allocations**

* Default: **OFF**
* When OFF: all Parties are eligible.
* When ON:

  * High Income countries remain visible,
  * but receive **zero allocation**,
  * and the total fund is redistributed among non-High-Income countries.

Add a one-line note below the checkbox:

> *“When enabled, High Income countries receive zero allocation and the remaining allocations are rescaled so the total fund remains unchanged.”*

---

### Data requirement

The dataframe must include:

* `wb_income_group` with a value **"High income"** for High Income countries.

---

### Calculation logic (mandatory)

Implement the eligibility filter **before normalisation**.

#### Step 1 — Define eligibility

```python
eligible = True
if exclude_high_income:
    eligible = wb_income_group != "High income"
```

Store this as a boolean column:

```python
df["eligible"] = eligible
```

---

#### Step 2 — Compute inverse weights **only for eligible rows**

```python
df["inv_weight"] = 0.0
df.loc[df["eligible"], "inv_weight"] = 1.0 / df.loc[df["eligible"], "un_share_fraction"]
```

---

#### Step 3 — Normalise over eligible rows only

```python
total_weight = df.loc[df["eligible"], "inv_weight"].sum()

df["inverted_share"] = 0.0
df.loc[df["eligible"], "inverted_share"] = (
    df.loc[df["eligible"], "inv_weight"] / total_weight
)
```

* Non-eligible rows keep `inverted_share = 0`

---

#### Step 4 — Apply fund size

```python
df["alloc_usd"] = df["inverted_share"] * fund_size
```

* High Income countries will now have **alloc_usd = 0**

---

#### Step 5 — Apply IPLC split (unchanged)

```python
df["iplc_usd"] = df["alloc_usd"] * iplc_share
df["state_usd"] = df["alloc_usd"] - df["iplc_usd"]
```

---

### Output expectations

* Total allocations across **all rows still equal the fund size**.
* High Income countries:

  * remain listed,
  * have allocation = 0,
  * are clearly marked as ineligible.
* All aggregation views (regions, EU block, income groups):

  * reflect the redistribution automatically.

---

### Visual clarity (recommended)

In tables:

* Add a column: **Eligibility status**

  * values: “Eligible” / “Not eligible (High Income)”
* Optionally grey out rows where allocation = 0.

---

### Validation checks (required)

* Sum of `alloc_usd` across all rows == fund size (within tolerance)
* All High Income rows have `alloc_usd == 0`
* No non-High-Income row has zero allocation unless UN share is missing

---

### Important constraint

Do **not**:

* remove High Income rows from outputs,
* adjust UN scale values,
* add smoothing, caps, or baseline blending.

This is a **pure eligibility toggle**, not a formula change.
