# Decision Engine Evaluation Report

**Overall Accuracy on 10 Sample Claims:** `30.0%`

## Decision Tree & Rule Hierarchy
The `DecisionEngine` evaluates claims using the following precedence order:

1. **Evidence Sufficiency Gate:**
   - If `evidence_standard_met` is `False` -> status is automatically **`not_enough_information`**.
2. **Contradiction Gates:**
   - If `'wrong_object'` or `'wrong_object_part'` is flagged -> status is **`contradicted`**.
   - If `'damage_not_visible'` is flagged or the visible issue is `'none'` -> status is **`contradicted`**.
   - If the VLM-detected issue explicitly conflicts with the claimed issue -> status is **`contradicted`**.
3. **Support Gate:**
   - If the detected object, visible part, and visible issue match the claim, and damage is present -> status is **`supported`**.
4. **Default Gate:**
   - Otherwise, status falls back to **`not_enough_information`**.

## Sample Case Outputs & Comparisons

### Case 0 (CAR)
- **Expected (Ground Truth):** `supported`
- **Predicted:** `contradicted`
- **Ground Truth Justification:** *"The image clearly shows a dent on the rear bumper and the user history does not add risk."*
- **Predicted Justification:** *"Claim contradicts image evidence. The claimed rear_bumper is visible but appears to have no damage."*
- **Correctness Match:** ❌ FAIL

### Case 1 (CAR)
- **Expected (Ground Truth):** `not_enough_information`
- **Predicted:** `supported`
- **Ground Truth Justification:** *"The submitted images do not reliably support the claim because the damaged close-up and the full vehicle view appear to be from different cars."*
- **Predicted Justification:** *"Claim supported by image evidence. A visible broken_part is present on the front_bumper."*
- **Correctness Match:** ❌ FAIL

### Case 2 (CAR)
- **Expected (Ground Truth):** `supported`
- **Predicted:** `contradicted`
- **Ground Truth Justification:** *"The image set supports the claim because the windshield crack is visible in the close-up."*
- **Predicted Justification:** *"Claim contradicts image evidence. The VLM detected glass_shatter on the windshield, which contradicts the claimed crack."*
- **Correctness Match:** ❌ FAIL

### Case 3 (CAR)
- **Expected (Ground Truth):** `supported`
- **Predicted:** `contradicted`
- **Ground Truth Justification:** *"The submitted image directly shows damage to the claimed side mirror."*
- **Predicted Justification:** *"Claim contradicts image evidence. The VLM detected glass_shatter on the side_mirror, which contradicts the claimed broken_part."*
- **Correctness Match:** ❌ FAIL

### Case 4 (CAR)
- **Expected (Ground Truth):** `contradicted`
- **Predicted:** `supported`
- **Ground Truth Justification:** *"The images show only minor rear bumper scratching, so the severe damage claim is contradicted. User history also shows several rejected claims."*
- **Predicted Justification:** *"Claim supported by image evidence. A visible broken_part is present on the rear_bumper."*
- **Correctness Match:** ❌ FAIL

### Case 5 (CAR)
- **Expected (Ground Truth):** `not_enough_information`
- **Predicted:** `not_enough_information`
- **Ground Truth Justification:** *"The submitted image shows another part of the car and does not provide evidence for the headlight claim."*
- **Predicted Justification:** *"The visible damage is on a different part than the claimed headlight. The image quality is insufficient (too blurry, cropped, or non-original) to verify the claim."*
- **Correctness Match:** ✅ PASS

### Case 6 (CAR)
- **Expected (Ground Truth):** `supported`
- **Predicted:** `supported`
- **Ground Truth Justification:** *"The clearer second image supports the claim by showing a dent on the door."*
- **Predicted Justification:** *"Claim supported by image evidence. A visible dent is present on the door."*
- **Correctness Match:** ✅ PASS

### Case 7 (CAR)
- **Expected (Ground Truth):** `contradicted`
- **Predicted:** `not_enough_information`
- **Ground Truth Justification:** *"The image shows severe front-end damage rather than a scratch on the hood, so it does not support the user's hood-scratch claim."*
- **Predicted Justification:** *"The visible damage is on a different part than the claimed hood."*
- **Correctness Match:** ❌ FAIL

### Case 8 (LAPTOP)
- **Expected (Ground Truth):** `supported`
- **Predicted:** `contradicted`
- **Ground Truth Justification:** *"The image directly shows a crack on the laptop screen."*
- **Predicted Justification:** *"Claim contradicts image evidence. The VLM detected glass_shatter on the screen, which contradicts the claimed crack."*
- **Correctness Match:** ❌ FAIL

### Case 9 (LAPTOP)
- **Expected (Ground Truth):** `supported`
- **Predicted:** `supported`
- **Ground Truth Justification:** *"The first image supports the claim because the hinge damage is visible."*
- **Predicted Justification:** *"Claim supported by image evidence. A visible broken_part is present on the screen."*
- **Correctness Match:** ✅ PASS

## Edge Cases Handled
- **Mismatch Contradictions:** A wrong-object-part or wrong-object flag is categorized as `contradicted` rather than `not_enough_information` because the visual evidence actively disproves the claimant's description.
- **Claim Insufficiencies:** If full-view images are missing or the image set represents mismatched cars, the evidence sufficiency gate overrides all other checks, yielding `not_enough_information` as required.
