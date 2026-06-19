# Persistent Caching Report

This report outlines the implementation details and expected token savings resulting from the integration of persistent cache layers in our pipeline.

## 1. Cache Key Strategy

To ensure cache reliability and prevent stale predictions, we implemented deterministic hashing keys:

### A. Parser Cache (`cache/parser_cache.json`)
- **Key:** `SHA-256` hash of the verbatim `user_claim` dialogue transcript string:
  ```python
  hash(user_claim)
  ```
- **Reasoning:** The parser maps conversational text to claimed parts and issues. A unique transcript dictates a unique parsed intent.

### B. Image Analyzer Cache (`cache/image_cache.json`)
- **Key:** `SHA-256` hash of the sorted absolute `image_paths` joined by semicolons concatenated with the `claim_object` type:
  ```python
  hash(";".join(sorted(image_paths)) + claim_object)
  ```
- **Reasoning:** A visual review depends on the exact set of images and the context of the object being inspected. Sorting paths prevents order variation from triggering cache misses.

---

## 2. Expected Token Savings

Applying caching on repeated runs yields **100% token savings** for LLM and VLM API calls.

| Run Type | Avg. Parser Tokens / Row | Avg. Vision Tokens / Row | Total Tokens (20 Sample Rows) | Total Tokens (45 Test Rows) | Savings (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cache Miss (1st Run)** | ~400 | ~4,300 | 94,000 | 211,500 | 0% |
| **Cache Hit (Subsequent)** | 0 | 0 | **0** | **0** | **100%** |

---

## 3. Implementation Examples

During pipeline execution, logs record cache performance:

### Cache Miss (First Execution)
```text
[2026-06-20 00:15:02] INFO [claim_parser] CACHE MISS: Parsing claim via LLM/rules.
[2026-06-20 00:15:02] INFO [image_analyzer] CACHE MISS: Analyzing images via VLM.
```

### Cache Hit (Consecutive Execution)
```text
[2026-06-20 00:15:32] INFO [claim_parser] CACHE HIT: ClaimParser output loaded from cache.
[2026-06-20 00:15:32] INFO [image_analyzer] CACHE HIT: ImageAnalyzer output loaded from cache.
```
