# Taxonomy Compatibility Evaluation Report

- **Old Accuracy (before compatibility layer):** `30.0%`
- **New Accuracy (after compatibility layer):** `40.0%`

## Mapping Rules & Compatibility Layers
We added a taxonomy compatibility layer in the Decision Engine to prevent close synonyms and related issues from being evaluated as false contradictions.

### Issue Compatibility Pairs
- `crack` ↔ `glass_shatter`
- `dent` ↔ `collision`
- `broken_part` ↔ `missing_part`
- `torn_packaging` ↔ `crushed_packaging`
- `water_damage` ↔ `stain`

### Object Part Compatibility Rules
- Displays are mapped to screens: `display` ↔ `screen` ↔ `lcd`.
- Bumpers with trunks are mapped to bumpers: `rear bumper and trunk` ↔ `rear_bumper`.
- Overlapping sub-strings or mirror strings match.

## Detailed Case Evaluations

### Case 0 (CAR)
- **Expected Status:** `supported`
- **Predicted Status:** `contradicted`
- **Correctness:** ❌ FAIL
- **Visible Issue / Part:** `unknown` / `rear_bumper`
- **Claimed Issue / Part:** `missing_part` / `rear_bumper`

### Case 1 (CAR)
- **Expected Status:** `not_enough_information`
- **Predicted Status:** `contradicted`
- **Correctness:** ❌ FAIL
- **Visible Issue / Part:** `unknown` / `unknown`
- **Claimed Issue / Part:** `broken_part` / `front_bumper`

### Case 2 (CAR)
- **Expected Status:** `supported`
- **Predicted Status:** `supported`
- **Correctness:** ✅ PASS
- **Visible Issue / Part:** `glass_shatter` / `windshield`
- **Claimed Issue / Part:** `crack` / `windshield`

### Case 3 (CAR)
- **Expected Status:** `supported`
- **Predicted Status:** `contradicted`
- **Correctness:** ❌ FAIL
- **Visible Issue / Part:** `glass_shatter` / `side_mirror`
- **Claimed Issue / Part:** `broken_part` / `side_mirror`

### Case 4 (CAR)
- **Expected Status:** `contradicted`
- **Predicted Status:** `not_enough_information`
- **Correctness:** ❌ FAIL
- **Visible Issue / Part:** `dent` / `unknown`
- **Claimed Issue / Part:** `broken_part` / `rear_bumper`

### Case 5 (CAR)
- **Expected Status:** `not_enough_information`
- **Predicted Status:** `not_enough_information`
- **Correctness:** ✅ PASS
- **Visible Issue / Part:** `none` / `side_mirror`
- **Claimed Issue / Part:** `broken_part` / `headlight`

### Case 6 (CAR)
- **Expected Status:** `supported`
- **Predicted Status:** `contradicted`
- **Correctness:** ❌ FAIL
- **Visible Issue / Part:** `unknown` / `unknown`
- **Claimed Issue / Part:** `dent` / `door`

### Case 7 (CAR)
- **Expected Status:** `contradicted`
- **Predicted Status:** `not_enough_information`
- **Correctness:** ❌ FAIL
- **Visible Issue / Part:** `broken_part` / `front_bumper`
- **Claimed Issue / Part:** `scratch` / `hood`

### Case 8 (LAPTOP)
- **Expected Status:** `supported`
- **Predicted Status:** `supported`
- **Correctness:** ✅ PASS
- **Visible Issue / Part:** `glass_shatter` / `screen`
- **Claimed Issue / Part:** `crack` / `screen`

### Case 9 (LAPTOP)
- **Expected Status:** `supported`
- **Predicted Status:** `supported`
- **Correctness:** ✅ PASS
- **Visible Issue / Part:** `broken_part` / `screen`
- **Claimed Issue / Part:** `broken_part` / `screen`

