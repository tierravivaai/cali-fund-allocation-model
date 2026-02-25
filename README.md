# Cali Allocation Model (UN Scale)

This interactive tool illustrates how Cali Fund allocations would be distributed if based on the **latest UN Scale of Assessments (2025-2027)**, inverted to reflect relative need.

## Features
- **Adjustable Fund Size**: Scale the annual Cali Fund from $0.002bn ($2m) to $10.0bn.
- **IPLC Earmark**: Set the percentage earmarked for Indigenous Peoples & Local Communities (50% to 80%).
- **Multi-perspective views**:
    - Detailed Party-level table.
    - Regional aggregations (UNSD M49).
    - EU Block summary.
    - Share by WB Income Group.
    - Developmental groupings (LDC, SIDS).
- **High Income Filter**: Ability to toggle High Income countries out of the allocation pool (enabled by default).
- **Transparency**: Toggle "Raw Inversion and Explanation" to see plain language and technical summaries of the methodology.

## Installation & Setup

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Methodology
The model takes each Party's UN Scale of Assessment share for 2027 and inverts it. This means countries with a smaller UN share (typically lower-income countries) receive a larger portion of the Cali Fund.

## Data Sources
- **UN Scale of Assessments**: General assembly resolution 79/225.
- **Regions**: UNSD M49 standard.
- **Income Class**: World Bank Country and Lending Groups.

## Floor Calculation (Minimum Share per Eligible Country)

### Purpose
The floor sets a minimum percentage of the total fund that each eligible country must receive under the allocation model.

It is designed to prevent extremely small allocations that may be operationally insignificant, particularly when the fund size is large and the inverted UN scale produces very small shares for some countries.

### How It Works
- The model first calculates each eligible country’s share using the inverted UN scale of assessment.
- If a country’s share falls below the selected floor percentage, it is raised to that minimum level.
- The remaining available funds are then redistributed proportionally across the other eligible countries so that total allocations still sum to 100% of the fund.

The floor applies only to eligible countries as defined by the model settings (e.g. exclusion of high-income countries if selected).

### Mathematical Constraint
The maximum feasible floor is determined dynamically by:
> **Maximum floor (%) = 100 ÷ number of eligible countries**

This ensures that the combined minimum shares do not exceed the total fund.
For example:
- If 150 countries are eligible, the maximum feasible floor is 0.67%.
- If 100 countries are eligible, the maximum feasible floor is 1.00%.

The slider is automatically limited to this value to ensure the model remains internally consistent.

### Interpretation
The floor does not represent entitlement or guaranteed disbursement.
It is a modelling parameter that illustrates how a minimum allocation rule would alter the distribution of resources under the inverted UN framework.

## Ceiling Calculation (Maximum Share per Eligible Country)

### Purpose
The ceiling sets a maximum percentage of the total fund that any eligible country may receive.

It is designed to limit concentration of funding among countries with very small UN assessment shares (which receive higher allocations under the inverted model).

### How It Works
- The model first calculates each eligible country’s share using the inverted UN scale.
- If a country’s share exceeds the selected ceiling percentage, it is reduced to that maximum level.
- The remaining funds are redistributed proportionally among the other eligible countries.
- Total allocations always sum to 100% of the fund.

The ceiling applies only to eligible countries under the current model settings.

### Interpretation
The ceiling does not impose a political cap or entitlement rule.
It is a scenario-setting tool that allows users to explore how limiting concentration affects overall distribution patterns.

Lower ceilings produce more even distributions.
Higher ceilings allow stronger differentiation under the inverted UN scale.

### Combined Effect of Floor and Ceiling
When both are enabled:
- Countries below the floor are lifted upward.
- Countries above the ceiling are reduced.
- Remaining funds are redistributed proportionally.
- The total allocation always remains equal to the total fund.

These parameters are illustrative modelling controls intended to explore distributional outcomes under different policy assumptions.

## Validation and Data Integrity

The model undergoes rigorous automated validation to ensure statistical accuracy and completeness. For statisticians and developers, the following checks are enforced on every update:

### 1. Party Count & Alignment
The model is validated against the **CBD COP16 Budget Table** (`cbd_cop16_budget_table.csv`) as the primary source of truth for CBD Parties.
- **Validation Rule**: Exactly **196 Parties** (including the European Union) must be present and correctly mapped.
- **Location**: `tests/test_logic.py` -> `test_cbd_party_count` and `test_budget_table_alignment`.

### 2. Metadata Completeness
Every record is checked to ensure no missing values for regional or economic classifications.
- **Validation Rule**: 100% of Parties must have an assigned **UN Region**, **WB Income Group**, and **LDC/SIDS status**.
- **Location**: `tests/test_logic.py` -> `test_metadata_completeness` and `test_strict_data_integrity`.

### 3. Allocation Consistency
The mathematical core ensures that the sum of individual allocations matches the user-defined fund size precisely.
- **Validation Rule**: `Sum(State Component + IPLC Component) = Total Fund Size`.
- **Location**: `tests/test_logic.py` -> `test_allocation_sums_to_fund_size` and `test_tiny_scenarios.py`.

### 4. Constraint Validation (Floor/Ceiling)
The model supports user-defined floor and ceiling constraints on individual party shares.
- **Validation Rule**: All eligible parties must receive a share within `[floor, ceiling]` while maintaining a total sum of 100%. The model handles iterative redistribution of shares when constraints are applied.
- **Dynamic Floor Check**: The UI automatically limits the maximum floor percentage to `100 / n_eligible` to prevent mathematical impossibility.
- **Location**: `tests/test_floor_ceiling.py`.

### 5. Cross-Reference Mapping
A systematic mapping layer (`manual_name_map.csv`) standardizes Party names across UN, World Bank, and CBD datasets.
- **Illustration of the Join Strategy**:
  ```sql
  SELECT 
      COALESCE(mapped.name, raw.name) as party,
      COALESCE(regions.name, fallback_regions.name) as region
  FROM parties
  LEFT JOIN name_map ON raw.name = name_map.party_raw
  LEFT JOIN unsd_regions ON mapped.name = unsd_regions.country
  ```
- **Location**: `logic/data_loader.py` -> `get_base_data()`.

## Testing
To run the validation suite locally:
```bash
python3 -m pytest
```
