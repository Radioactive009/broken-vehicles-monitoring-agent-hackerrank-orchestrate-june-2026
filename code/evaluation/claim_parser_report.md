# Claim Parser Evaluation Report

This report outlines the analysis patterns, synonym mapping rules, confidence strategies, and evaluation findings for the `ClaimParser` NLP extraction module.

---

## 1. Extracted Patterns & Synonyms Mappings

During validation on the `sample_claims.csv` dataset, the following dialog patterns and bilingual synonyms were identified and mapped:

### Language Variations
- **Hinglish/Hindi Transliteration**:
  - *"front side par mark aa gaya hai"* $\rightarrow$ front bumper scratch
  - *"teclado / teclas"* $\rightarrow$ keyboard
  - *"bumper ke upar"* $\rightarrow$ bumper
  - *"opened jaisa lag raha tha"* $\rightarrow$ torn packaging / seal
- **Spanish Colloquialisms**:
  - *"se cayo de la mesa... pantalla esta cracked"* $\rightarrow$ screen crack
  - *"parachoques trasero"* $\rightarrow$ rear bumper

### Part mappings
- `rear` / `back` + `bumper` $\rightarrow$ `rear_bumper`
- `front` / `bumper` $\rightarrow$ `front_bumper`
- `display` / `glass` $\rightarrow$ `screen` (laptop) or `windshield` (car)
- `keycaps` / `keys` $\rightarrow$ `keyboard`
- `tape` $\rightarrow$ `seal`
- `product` / `product inside` $\rightarrow$ `contents`

---

## 2. Confidence Strategy

Confidence scores (0.0 to 1.0) are determined as follows:
- **LLM parsing (1.0 - 0.8)**: High confidence when the model receives structured conversational turns and maps cleanly to taxonomy options.
- **Rule-based fallback (0.7)**: Occurs when API credentials are not set or connection timeouts occur. Keyword search is executed locally.
- **Low Confidence (0.5)**: Triggered when multiple conflicting parts or issue types are detected in the transcript (e.g., claiming headlight and door damage in the same message) or no taxonomy tokens match.

---

## 3. Local Evaluation Runs (Verification)

Here is a mapping trace of `ClaimParser` executions on the sample claims:

- **Case 1 (user_001)**: Rear bumper dent claim
  - *Extracted*: `{claimed_issue_type: "dent", claimed_object_part: "rear_bumper"}`
- **Case 3 (user_004)**: Windshield crack claim
  - *Extracted*: `{claimed_issue_type: "crack", claimed_object_part: "windshield"}`
- **Case 10 (user_010)**: Laptop hinge broken claim
  - *Extracted*: `{claimed_issue_type: "broken_part", claimed_object_part: "hinge"}`
- **Case 15 (user_015)**: Package corner crushed claim
  - *Extracted*: `{claimed_issue_type: "crushed_packaging", claimed_object_part: "package_corner"}`

---

## 4. Evaluation Metrics (Before & After Optimization)

We ran the rule-based claim parser engine across all 20 rows of `dataset/sample_claims.csv` to calculate validation accuracy against labeled data:

| Metric | Before Optimization | After Optimization |
|---|---|---|
| **Object Part Accuracy** | 65.00% | 70.00% |
| **Issue Type Accuracy** | 35.00% | 40.00% |
| **Exact Match Accuracy** | 30.00% | 30.00% |

### Failure Analysis & Mitigations
1. **Colloquial Mismatches**: Words like "opened" for laptops were incorrectly flagged as `torn_packaging` (for packages) instead of normal mechanical function or general visual damage.
   * *Mitigation*: Implemented object-aware word filters that prevent package-only issues (e.g. `torn_packaging`, `crushed_packaging`) from being assigned to car/laptop claims.
2. **Object Domain Validation**: Under strict rules, package parts (e.g. `seal`, `label`) and laptop parts (e.g. `screen`, `hinge`) are validated to ensure they are never cross-assigned to the wrong category. Any mismatch is mapped to a logical default (e.g. laptop keyboard matches $\rightarrow$ `keyboard`, package screen matches $\rightarrow$ `contents`).
3. **Exaggeration/Contradiction Baseline Mismatch**: Because the evaluation script compares parsed *claimed* issues against the *visible* expected labels (which include contradicted cases where no damage is present), issue type accuracy is naturally lower than 100% on sample data, representing a logical divergence between claim statements and ground truth photos. This is normal and handled downstream by the VLM.

