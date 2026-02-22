# Cali Allocation Model (UN Scale)

This interactive tool illustrates how Cali Fund allocations would be distributed if based on the **latest UN Scale of Assessments (2025-2027)**, inverted to reflect relative need.

## Features
- **Adjustable Fund Size**: Scale the annual Cali Fund from $0.1bn to $10.0bn.
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

### 4. Cross-Reference Mapping
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
