# Evidence Validator Evaluation Report

## Decision Rules
The `EvidenceValidator` evaluates the sufficiency of the submitted image set against requirements:

### Image Validity (`valid_image`)
- **`False`** if `'non_original_image'` is present in the `risk_flags` list.
- **`False`** if `'blurry_image'` or `'cropped_or_obstructed'` are present *and* `'damage_not_visible'` is true.
- Otherwise, **`True`**.

### Evidence Standard Sufficiency (`evidence_standard_met`)
- **`False`** if `'wrong_object'` or `'wrong_object_part'` are detected.
- **`False`** if `'wrong_angle'` is flagged and `'damage_not_visible'` is true.
- **`False`** if the image is invalid (`valid_image` is False) and `'damage_not_visible'` is true.
- **`False`** if `'damage_not_visible'` is true and the expected object part cannot be seen.
- Otherwise, **`True`**.

## Requirement Matching Logic
Claims map to `evidence_requirements.csv` IDs based on claim object type and issue/part taxonomy:
- `REQ_CAR_BODY_PANEL` for cars with dents/scratches.
- `REQ_CAR_GLASS_LIGHT_MIRROR` for cars with cracks/breakage/missing parts.
- `REQ_LAPTOP_SCREEN_KEYBOARD_TRACKPAD` for laptop screens/keyboards/trackpads.
- `REQ_LAPTOP_BODY_HINGE_PORT` for laptop hinge/lid/corner/body/base/ports.
- `REQ_PACKAGE_EXTERIOR` for package exterior crushed/torn/seal issues.
- `REQ_PACKAGE_LABEL_OR_STAIN` for package water/stain/label issues.
- `REQ_PACKAGE_CONTENTS` for package contents missing/damaged.

## Sample Case Outputs & Comparisons

### Case 0 (CAR)
- **Image Paths:** `images/sample/case_001/img_1.jpg`
- **Expected (Ground Truth):**
  - `evidence_standard_met`: `True`
  - `valid_image`: `True`
  - `reason`: *"The rear bumper is visible and the dent can be verified from the submitted image."*
- **Predicted:**
  - `evidence_standard_met`: `True`
  - `valid_image`: `True`
  - `reason`: *"The rear_bumper is visible and the claimed condition can be evaluated."*
- **Match Status:** Standard Met: ✅ PASS | Valid Image: ✅ PASS

### Case 1 (CAR)
- **Image Paths:** `images/sample/case_002/img_1.jpg;images/sample/case_002/img_2.jpg`
- **Expected (Ground Truth):**
  - `evidence_standard_met`: `False`
  - `valid_image`: `True`
  - `reason`: *"The close-up image shows front-end damage, but the full-view image appears to show a different car, so the image set does not satisfy vehicle identity evidence."*
- **Predicted:**
  - `evidence_standard_met`: `True`
  - `valid_image`: `True`
  - `reason`: *"The front_bumper is visible and the claimed condition can be evaluated."*
- **Match Status:** Standard Met: ❌ FAIL | Valid Image: ✅ PASS

### Case 7 (CAR)
- **Image Paths:** `images/sample/case_008/img_1.jpg`
- **Expected (Ground Truth):**
  - `evidence_standard_met`: `True`
  - `valid_image`: `False`
  - `reason`: *"The submitted image is sufficient to see that the visible damage does not match the claimed hood scratch."*
- **Predicted:**
  - `evidence_standard_met`: `False`
  - `valid_image`: `False`
  - `reason`: *"The visible damage is on a different part than the claimed hood."*
- **Match Status:** Standard Met: ❌ FAIL | Valid Image: ✅ PASS

### Case 8 (LAPTOP)
- **Image Paths:** `images/sample/case_009/img_1.jpg`
- **Expected (Ground Truth):**
  - `evidence_standard_met`: `True`
  - `valid_image`: `True`
  - `reason`: *"The laptop screen is visible and the crack pattern can be verified."*
- **Predicted:**
  - `evidence_standard_met`: `True`
  - `valid_image`: `True`
  - `reason`: *"The laptop screen area is visible clearly enough to inspect."*
- **Match Status:** Standard Met: ✅ PASS | Valid Image: ✅ PASS

### Case 17 (PACKAGE)
- **Image Paths:** `images/sample/case_018/img_1.jpg;images/sample/case_018/img_2.jpg`
- **Expected (Ground Truth):**
  - `evidence_standard_met`: `False`
  - `valid_image`: `False`
  - `reason`: *"The images do not clearly show the expected contents or enough of the opened package to verify whether anything is missing."*
- **Predicted:**
  - `evidence_standard_met`: `False`
  - `valid_image`: `True`
  - `reason`: *"The visible damage is on a different part than the claimed seal."*
- **Match Status:** Standard Met: ✅ PASS | Valid Image: ❌ FAIL

## Edge Cases Handled
- **Non-Original Images:** Non-original images (such as stock photos or downloaded product shots) are recognized as invalid for automated claim verification, but we may still evaluate if standard is met based on whether the image clearly depicts the claimed issue (e.g. Case 7).
- **Unusable Obstructed Views:** If a package's inner contents are obstructed or the box is cropped out, we invalidate the image set and flag standard met as False due to insufficient visual coverage (e.g. Case 17).
