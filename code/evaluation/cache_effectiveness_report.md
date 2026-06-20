# Cache Effectiveness Report

This report evaluates the current status and effectiveness of the persistent caching mechanism on the sample claims dataset (`dataset/sample_claims.csv`).

## 1. Cache Entry Statistics
* **parser_cache.json**: 1 entry
* **image_cache.json**: 1 entry

## 2. Hit and Miss Analysis
Based on the execution logs:
* **Total Parser Cache Hits**: 0
* **Total Parser Cache Misses**: 0
* **Total Image Cache Hits**: 0
* **Total Image Cache Misses**: 0

*Note: Since the evaluation has not yet successfully completed across the full sample set in this environment, no hits or misses are recorded in the active run logs beyond initial checks.*

## 3. Live API Call Estimation
* **Total claims in `sample_claims.csv`**: 20
* **Claims requiring live API calls**: **19 claims**

## 4. Explanations for Missing Cache Entries
Since more than 3 claims still require live API calls, the lack of cached entries is due to the following factors:
1. **Incomplete Runs**: Previous evaluation runs did not complete successfully for all 20 rows because they were aborted or corrupted by API authentication (401) and rate limits (429) before writing to the cache file.
2. **Cache-on-Success Logic**: The pipeline only updates the persistent cache when an API call completes successfully. Since the API key in the environment returns `401 Unauthorized`, almost all VLM requests ended in errors and fell back to default schemas, which are not saved in the cache to avoid caching incorrect placeholder predictions.
