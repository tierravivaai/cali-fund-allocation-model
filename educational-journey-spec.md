# Cali Fund Educational Dashboard Journey

## Problem Statement
The current dashboard jumps directly to a complex model with all parameters visible at once. Users need an educational journey that:
1. Shows the Understand the relationship between CBD budget percentages and Cali Fund shares
- Visualizes that Parties with lowest CBD contributions become highest allocations under raw inversion
- Demonstrates why moderation mechanisms are necessary
- Introduces parameters incrementally with clear visual feedback

## Important Design Principle: Neutral Terminology

Throughout this educational journey:
- Use "allocations" instead of "winners"/"losers"/"biggest winners"/"biggest losers"
- Use "increases"/"decreases" instead of "winners"/"losses"
- Use "Party positions" or "ranking" instead of "top"/"bottom"
- Use neutral, objective language throughout (no "worst", "best", "first", "last")

## Target Users

## Target Users
- CBD negotiators unfamiliar with allocation models
- Delegates who need quick intuition about the outcomes
- Anyone reviewing the understand equity vs. ability-to-pay logic

## Proposed Journey Flow

### Phase 1: Raw Inversion Explorer (The "Ah-ha!" Moment)

**Goal:** Show users what pure inverse looks like and why it's impractical

**Features:**
- **Panel: Raw Inversion Results**
  - Display table showing: Party, CBD Budget %, Raw Share, Allocation (USDM)
  - Sorted by Raw Share (descending)
  - Top 10 and Bottom 10 highlighted differently
  - Total fund: $1B (adjustable)

- **Panel: Distribution Graph**
  - Bar chart showing Raw Share for all Parties
  - Color coding:
    - Green: Top 10 allocations by allocation
    - Red: Bottom 10 by allocation
    - Gray: Middle range
  - X-axis: Party name
  - Y-axis: Allocation USD Millions

- **Panel: Summary Statistics**
  - Total number of Parties
  - Extreme outcomes indicators:
    - Top allocation share (Party name + %)
    - Bottom allocation share (Party name + %)
    - Ratio between highest and lowest allocation

- **Educational Note:** 
  - "Notice: Parties with lowest CBD Budget percentages get the highest allocations under raw inversion. This illustrates why moderation mechanisms (smoothing, caps, lower bounds) are needed."

**No controls exposed yet** - this is pure display of the understand the the problem

---

### Phase 2: Moderation Introduction (The "Why We Need Safety First" Moment)

**Goal:** Introduce FIRST moderation mechanism with visual before/after comparison

**Features:**
- **Panel: Add Smoothing**
  - Toggle: "Apply Smoothing (exponent)"
  - Slider: Smoothing Exponent (range: 0.1 to 2.0, default 0.5)
  - Side-by-side comparison:
    - Left: Raw results (frozen at Phase 1 state)
    - Right: With smoothing applied
  - Highlight rows with significant changes
  - Show summary metrics at top:
    - Most improved Party
    - Most disadvantaged Party
    - Range compression indicator

- **Panel: Smoothing Explanation**
  - Interactive text explaining what smoothing does:
    - "Smoothing uses exponent-based dampening..."
    - "Higher value = more compression of extremes..."
  - Visual comparison of top Party shares before/after

- **Educational Note:**
  - "Smoothing reduces extreme outcomes by compressing the range between highest and lowest allocations."

**Controls exposed:**
- Smoothing Exponent slider

---

### Phase 3: Add Lower Bound Protection (The "Protecting the Vulnerable Parties" Moment)

**Goal:** Show how lower bound prevents micro-contributors from dominating

**Features:**
- **Panel: Add Lower Bound**
  - Toggle: "Apply Lower Bound"
  - Slider: Lower Bound % (range: 0.001% to 0.5%, default 0.01%)
  - Side-by-side bar chart:
    - X-axis: Raw vs Lower Bound Share
    - Y-axis: Allocation USD Millions
    - Top 5 affected Parties highlighted
  
- -**Panel: Affected Parties Table**
  - Shows Parties whose allocation changed due to lower bound
  - Columns: Party, Raw Share, New Share, Difference
  - Sorted by impact magnitude

- **Educational Note:**
  - "Lower bound prevents micro-contributors (small CBD Budget%) from getting disproportionately large allocations, protecting vulnerable Parties."

**Controls exposed:**
- Smoothing Exponent slider (carry over from Phase 2)
- Lower Bound slider

---

### Phase 4: Add Cap Mechanism (The "Preventing Monopolies" Moment)

**Goal:** Show how cap prevents any single Party from dominating

**Features:**
- **Panel: Add Cap**
  - Toggle: "Apply Cap"
  - Slider: Maximum Cap % (range: 0.5% to 10%, default 2%)
  - Two charts:
    - Pie chart of allocations (Top 10 by allocation colored differently, "others" lumped)
    - Bar chart showing top 10 capped parties with uncapped allocation reference line
 - Animated comparison slider: drag slider to show cap move in real-time

- **Panel: Cap Statistics**
  - Count of Parties at cap
  - Total allocation lost to capping
  - Share captured by top N Parties

- **Educational Note:**
  - "Cap prevents any single Party from dominating, ensuring proportional distribution."

**Controls exposed:**
- Smoothing Exponent slider (carry over)
- Lower Bound slider
- Cap slider

---

### Phase 5: Add Baseline Blend (The "Supporting the Middle-Income" Moment)

**Goal:** Show how baseline blend supports middle-income developing countries

**Features:**
- **Panel: Add Baseline Blend**
  - Toggle: "Apply Baseline Blend"
  - Slider: Baseline Blend Share % (range: 0% to 50%, default 20%)
  - Toggle: Baseline Eligibility (developing Parties / all Parties)
  - Before/after comparison table showing:
    - Parties by development category
    - Allocation amounts before/after baseline
    - Percentage change per category

- **Panel: Beneficiary Analysis**
  - Bar chart comparing allocations:
    - LDC vs other categories
    - Party position changes by category after baseline
    - Top Party position gains in each category

- **Educational Note:**
  - "Baseline blend allocates a portion equally to LDC Parties, reducing extreme concentration and supporting more equitable distribution."

**Controls exposed:**
- Smoothing Exponent slider (carry over)
- Lower Bound slider
- Cap slider
- Baseline Blend share slider
- Baseline Eligibility toggle

---

### Phase 6: Consolidated Working Model (The "Explore Trade-offs" Moment)

**Goal:** All controls together, enable users to explore trade-offs

**Features:**
- All controls from Phases 2-5 in a single view
- **Panel: Working Scenario Summary**
  - Current parameter configuration summary
  - Key metrics highlights
- **Panel: Working Scenario Table**
  - Full country-level results
  - Sortable columns
  - Filterable by region/status/IPLC/SIDS
- **Panel: Trade-off Dashboard**
  - Interactive charts showing:
    - Top/bottom allocations by controls
    - Allocation by status with sliders
    - IPLC envelope by controls

- **Panel: Comparison vs Reference**
  - Only appears if different from reference
  - Top increases/decreases
  - Side-by-side charts for key metrics

- **Educational Note:**
  - "Explore how different parameters affect distribution and Party outcomes."

**All controls exposed in Phase6:**
- Fund Size slider
- IPLC Share slider (min locked at 50%)
- Smoothing Exponent slider
- Lower Bound slider
- Cap slider
- Baseline Blend Share slider
- Baseline Eligibility toggle

---

## Implementation Approach

### As Distinct PRs (Recommended for clarity and easy review)

#### PRD #1: Raw Inversion Explorer + Dashboard Restructure
**Changes:**
- Create new dashboard structure with phase-based navigation
- Implement Phase1 functionality (Raw Inversion Explorer)
- Clean up duplicate code from current dashboard.py
- Add simple "Next Phase" button to progress through phases
- Remove all parameter sliders initially (only Fund Size)

**Files modified:**
- dashboard.py → Complete restructure with phase-based layout
- New: calculate_raw_inversion.py function

**Estimated effort:** 3 hours

---

#### PRD #2: Add Smoothing Journey (Phase 2)
**Changes:**
- Implement Phase2 functionality
- Add Phase2 UI with side-by-side comparison
- Add smoothing exponent slider and explainers
- Update navigation/fund to Phase2

**Files modified:**
- dashboard.py (add Phase2)
- No SQL model changes

**Estimated effort:** 2 hours

---

#### PRD #3: Add Lower Bound Protection Journey (Phase3)
**Changes:**
- Implement Phase3 functionality
- Add lower bound slider with before/after comparison
- Add affected Parties table
- Update navigation to Phase3

**Files modified:**
- dashboard.py (add Phase3)

**Estimated effort:** 2 hours

---

#### PRD #4: Add Cap Mechanism Journey (Phase4)
**Changes:**
- Implement Phase4 functionality
- Add cap slider with pie chart
- Add animated comparison slider
- Add cap statistics panel
- Update navigation to Phase4

**Files modified:**
- dashboard.py (add Phase4)

**Estimated effort:** 2 hours

---

#### PRD #5: Add Baseline Blend Journey (Phase5)
**Changes:**
- Implement Phase5 functionality
- Add baseline blend slider and eligibility toggle
- Add受益iciary Analysis panel
- Update navigation to Phase5

**Files modified:**
- dashboard.py (add Phase5)

**Estimated effort:** 2 hours

---

#### PRD #6: Consolidated Working Model (Phase6)
**Changes:**
- Implement Phase6 functionality (all controls together)
- Add trade-off dashboard
- Add comparison only when different from reference
- Update navigation to Phase6 (final)
- Ensure consistency between all phases

**Files modified:**
- dashboard.py (add Phase6)
- Possibly model updates if needed

**Estimated effort:** 3 hours

---

## Key Design Decisions

### Navigation
- Sidebar shows current phase and progress (Phase 1 of 6)
- "Next Phase" button advances user through journey
- Can also jump between phases using dropdown selector

### Progressive Controls
- Controls only appear when relevant
- Later phases inherit controls from earlier phases
- Controls always show current values (state persistence)

### Color Coding
- Phase1: Highlighted allocations (top 10 high vs top 10 low positions), Neutral color scheme
- All phases use consistent color scheme
- Changes/deltas highlighted using color

### Data Display
- All phases show USD Millions as primary unit
- IPLC allocation always visible
- State allocation always visible

### Technical Debt
- Remove current duplicate code in dashboard.py
- Consolidate data loading logic
- Make Phase1 to Phase6 consistent data structure where possible

---

## Success Criteria
- User can complete all 6 phases in 5-10 minutes
- User understands why each moderation mechanism exists
- User can intuitively predict impact of changing each parameter
- Dashboard is clean, consistent, and maintainable
