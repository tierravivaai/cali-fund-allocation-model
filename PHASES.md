### Phase 1 — Freeze scope and governance (do this first)

**Outcome:** everyone agrees what is being built and what is *not* being debated anymore.

1. **Freeze the Objectives Brief**

   * Save the last version as `OBJECTIVES.md` in the repo root.
   * State explicitly: *“This document is authoritative over code comments and dashboards.”*
   * No more conceptual changes unless something is legally wrong.

2. **Define a single “reference scenario”**
   This is not a recommendation — it’s a baseline for comparison.

   * Fund size: USD 1bn/year
   * IPLC share: 50%
   * Smoothing exponent: 0.5
   * Lower bound: 0.01%
   * Cap: 2%
   * Baseline blend: 20% to LDC Parties
   * Baseline eligibility: LDC Parties

   This gives reviewers something concrete to react to.

---

### Phase 2 — Implement the core model (DuckDB + SQL)

**Outcome:** one trusted calculation engine that everything else depends on.

3. **Create the DuckDB model**

   * Inputs:

     * `cbd_assessed_contributions.csv`
     * `unsd_m49.csv`
     * `eu27.csv`
     * `manual_name_map.csv` (if needed)
   * Implement `allocation.sql` (the skeleton you already have).
   * Produce:

     * `allocation_country_internal`
     * `allocation_country_public`
     * region / subregion / intermediate aggregations
     * EU27 + European Union aggregation
     * SIDS

4. **Add basic validation checks**
   These are essential for credibility:

   * allocations sum to fund size
   * IPLC + State = total
   * no Party exceeds the cap
   * no missing UNSD regions (report list explicitly)

5. **Lock the calculation**

   * Tag the commit.
   * Treat this as the **reference engine**.
   * Any UI change must call this logic, not reimplement it.

---

### Phase 3 — Rapid exploration interface (Streamlit)

**Outcome:** something you can use live with colleagues and delegates.

6. **Build a Streamlit app (thin layer)**
   The app should do *nothing clever* — just expose parameters.

   Required controls:

   * Fund size (slider)
   * IPLC share (slider)
   * Smoothing exponent (slider)
   * Lower bound (slider)
   * Cap (slider)
   * Baseline blend (slider)
   * Baseline eligibility (toggle)

7. **Default views in Streamlit**

   * Country table (alphabetical, searchable)
   * Region totals
   * EU27 + EU total
   * Developed vs LDC totals
   * IPLC envelope totals (global + per group)

8. **Add a “What changed?” panel**

   * Show delta vs reference scenario.
   * This is hugely helpful politically: *“what moved, and why.”*

---

### Phase 4 — Review and stress-test

**Outcome:** confidence that this won’t collapse in a room full of diplomats.

9. **Stress-test the extremes**

   * Very low lower bound (what breaks?)
   * No smoothing (show why it’s unacceptable)
   * High baseline (who benefits?)
   * Tight cap (who is constrained?)

10. **Prepare a short reviewer note**
    One page:

* What the sliders do
* What problems they solve
* What trade-offs they introduce

This becomes your **“how to read the model” handout**.

---

### Phase 5 — Formalisation (only after iteration)

**Outcome:** something that can sit behind COP language.

11. **Port stable outputs to Superset (optional)**

* Only once assumptions settle.
* Superset = presentation and monitoring
* Streamlit = exploration and negotiation

12. **Draft neutral COP-style explanatory text**

* No numbers
* No winners/losers
* Just method, principles, and safeguards

---

## Decision you *don’t* need to make yet

* Exact IPLC delivery mechanisms
* Final cap value
* Whether baseline is 10%, 20%, or 30%

Those are **political outcomes**, not modelling prerequisites.

---

## What I recommend you do *now*

1. Tell the droid:
   **“Implement Phase 2 and Phase 3 exactly as written.”**
2. Use Streamlit internally for a week.
3. Only then worry about polishing or external sharing.

If you want, next I can:

* write the **Streamlit app skeleton**, or
* create a **review checklist** (“questions Parties will ask and where the model answers them”).
