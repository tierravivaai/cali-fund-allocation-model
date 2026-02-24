## Worked example: step-by-step calculation

This example shows how the model converts UN assessed shares into indicative allocations.

### Step 1: UN assessed shares (as published)

Assume the following UN Scale of Assessments shares:

* **Country A (LDC - Low Income):** 0.005%
* **Country B (Upper Middle Income):** 2.90%
* **Country C (Upper Middle Income):** 20.00%

These values are **percentages**, as published in the UN scale.

---

### Step 2: Convert percentages to standard numbers

Before inversion, percentages are converted into standard numerical values by dividing by 100.

* **Country A:**
  0.005% → 0.00005

* **Country B:**
  2.90% → 0.029

* **Country C:**
  20.00% → 0.20

This conversion is a **technical step** to allow the calculation to proceed correctly.

---

### Step 3: Invert the values (calculate weights)

Next, the model takes the reciprocal (1 divided by the value) for each country.

* **Country A:**
  1 ÷ 0.00005 = **20,000**

* **Country B:**
  1 ÷ 0.029 ≈ **34.48**

* **Country C:**
  1 ÷ 0.20 = **5**

These numbers are **weights**, not shares of the fund.

---

### Step 4: Normalise the weights into shares

The weights are summed and each country’s weight is divided by the total.

Total weight:
20,000 + 34.48 + 5 = **20,039.48**

Indicative shares:

* **Country A:**
  20,000 ÷ 20,039.48 ≈ **99.80%**

* **Country B:**
  34.48 ÷ 20,039.48 ≈ **0.17%**

* **Country C:**
  5 ÷ 20,039.48 ≈ **0.02%**

All shares together sum to **100%**.

*(In the full model, this calculation is performed across all eligible Parties, not just three.)*

---

### Step 5: Apply the fund size

Assuming a total fund size of **USD 1 billion per year**:

* **Country A:**
  ≈ USD **998.0 million**

* **Country B:**
  ≈ USD **1.7 million**

* **Country C:**
  ≈ USD **0.2 million**

---

### Step 6: Apply the IPLC earmark (illustrative)

If we assume **50%** of each allocation is earmarked for Indigenous Peoples and Local Communities (IPLCs):

* **Country A:**
  ≈ USD **499.0 million** IPLC component
  ≈ USD **499.0 million** State component

* **Country B:**
  ≈ USD **0.85 million** IPLC component
  ≈ USD **0.85 million** State component

* **Country C:**
  ≈ USD **0.10 million** IPLC component
  ≈ USD **0.10 million** State component

---

## What this example illustrates

* Raw inversion strongly favours countries with **very small UN assessed shares**.
* Countries with **large assessed shares** receive relatively small allocations.
* The final allocations always sum exactly to the **total fund size**.
* This example shows **why balance points for middle-income countries may need to be discussed** to find the right 
balance.