# Risk Engine Evaluation Report

## Risk Scoring Rules & Thresholds
The `RiskEngine` loads user profiles from `user_history.csv` and implements standard checks:

### User History Risk (`user_history_risk`)
Flagged if the user matches any of the following parameters:
- Total past claims $\ge 10$.
- Total rejected claims $\ge 2$.
- Last 90 days claims $\ge 3$.
- Profile explicitly carries the `'user_history_risk'` flag in `history_flags`.

### Manual Review Required (`manual_review_required`)
Escalated if:
- Profile explicitly carries the `'manual_review_required'` flag in `history_flags`.
- Total rejected claims $\ge 3$.
- Any VLM mismatch (e.g. `'wrong_object'`) occurs *and* user has elevated history risk.
- Prompt injection is detected (`'text_instruction_present'`).
- Multiple concurrent visual risk factors are present.
- Evidence is insufficient to verify (`evidence_standard_met` is False or `valid_image` is False).

## Sample Case Outputs & Comparisons

### Case 0 (User: user_001, Object: CAR)
- **Image Paths:** `images/sample/case_001/img_1.jpg`
- **Expected (Ground Truth) Risk Flags:** `none`
- **Predicted Risk Flags:** `damage_not_visible;claim_mismatch`
- **Match Status:** ❌ FAIL

### Case 1 (User: user_002, Object: CAR)
- **Image Paths:** `images/sample/case_002/img_1.jpg;images/sample/case_002/img_2.jpg`
- **Expected (Ground Truth) Risk Flags:** `wrong_object;claim_mismatch;manual_review_required`
- **Predicted Risk Flags:** `cropped_or_obstructed`
- **Match Status:** ❌ FAIL

### Case 4 (User: user_005, Object: CAR)
- **Image Paths:** `images/sample/case_005/img_1.jpg;images/sample/case_005/img_2.jpg`
- **Expected (Ground Truth) Risk Flags:** `claim_mismatch;user_history_risk;manual_review_required`
- **Predicted Risk Flags:** `cropped_or_obstructed;wrong_object_part;claim_mismatch;user_history_risk;manual_review_required`
- **Match Status:** ❌ FAIL

### Case 7 (User: user_008, Object: CAR)
- **Image Paths:** `images/sample/case_008/img_1.jpg`
- **Expected (Ground Truth) Risk Flags:** `claim_mismatch;non_original_image;user_history_risk;manual_review_required`
- **Predicted Risk Flags:** `cropped_or_obstructed;low_light_or_glare;wrong_object_part;claim_mismatch;non_original_image;user_history_risk;manual_review_required`
- **Match Status:** ❌ FAIL

### Case 18 (User: user_033, Object: PACKAGE)
- **Image Paths:** `images/sample/case_019/img_1.jpg`
- **Expected (Ground Truth) Risk Flags:** `wrong_object;claim_mismatch;user_history_risk;manual_review_required`
- **Predicted Risk Flags:** `blurry_image;cropped_or_obstructed;wrong_object_part;claim_mismatch;user_history_risk;manual_review_required`
- **Match Status:** ❌ FAIL

## Edge Cases Handled
- **New Users:** If a user has no historical records in `user_history.csv`, they are assigned zero risk scoring defaults, ensuring new customers are processed fairly without false history flags.
- **Glared or Obstructed Views:** Quality flags from the VLM (glare, blur) are integrated to evaluate usability. If the VLM flags multiple visual flaws, the risk engine automatically escalates the claim for manual review.
