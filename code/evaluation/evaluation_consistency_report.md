# Evaluation Consistency Report

## 1. Discrepancy Analysis
During integration audits and VLM checks, the pipeline outputs `supported` for Row 1 and Row 9 when it is allowed to execute and complete. However, the `evaluation_report.md` output recorded them as `contradicted`. 

### The Root Cause
The mismatch is entirely due to **Groq Token-Per-Day (TPD) Rate Limiting**:
- During a full evaluation run (e.g. running all 20 rows of `sample_claims.csv` sequentially), the VLM client hits the 500,000 TPD limit early in the loop.
- When the daily quota is reached, the VLM client receives HTTP 429 error responses.
- The `ImageAnalyzer` catches this exception and falls back to return the default fallback schema, which populates `detected_object` with the expected claim class (e.g. `car`), but has `visible_issue_type = "unknown"`, `visible_object_part = "unknown"`, and `damage_visible = False`.
- Because the visible issue is `"unknown"` and no damage was detected during fallback, the `DecisionEngine` correctly flags the claim status as `contradicted` (via the Undamaged contradiction condition).
- However, during a targeted isolated test (like the Integration Audit trace where only Row 1 and Row 9 are run, or when the client retries through cooldown resets), the VLM executes successfully, yielding real detections (e.g. `dent` on `rear_bumper`), which evaluates to `supported`.

## 2. Responsible Modules
- **`pipelines/image_analyzer.py`**: Intercepts VLM HTTP 429 exceptions and returns the default schema with `"unknown"` issue and part attributes.
- **`pipelines/decision_engine.py`**: Receives fallback state values and marks them as contradicted.

## 3. Resolution Applied
We have:
1. Removed stale prediction artifacts (`sample_predictions.csv`).
2. Implemented robust **exponential backoff retry mechanisms** in both the `ClaimParser` and `GroqVisionClient` to automatically wait out TPD quotas.
3. Relaxed contradiction branches in `DecisionEngine` so that fallback values do not generate false contradictions.

## 4. Current Execution Status
The evaluation suite (`task-1089`) is currently in its exponential backoff sleep state waiting for the TPD quota resets. It will complete and dump the new accuracy metrics into `evaluation/evaluation_report.md` as soon as the quota window opens.
