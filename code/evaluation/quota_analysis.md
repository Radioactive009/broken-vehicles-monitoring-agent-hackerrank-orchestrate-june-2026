# Quota & Token Consumption Analysis Report

This document outlines token usage, API request counts, and quota projections for executing the multi-modal evidence review pipeline on Groq's API platform.

## 1. Request & Image Counts

We analyze the total rows and referenced image paths in both datasets to count the exact number of LLM and VLM API calls required.

| Dataset | Total Rows (Claims) | Total Images | Avg. Images / Claim | Parser Calls (LLM) | Vision Calls (VLM) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **sample_claims.csv** | 20 | 30 | 1.50 | 20 | 20 |
| **claims.csv** (test) | 45 | 78 | 1.73 | 45 | 45 |
| **Total** | **65** | **108** | **1.66** | **65** | **65** |

---

## 2. Token Size Estimations

We estimate the typical prompt and image token consumption per claim processed:

### LLM Claim Parser Call (`meta-llama/llama-4-scout-17b-16e-instruct`)
- **System Prompt & Instructions:** ~200 tokens
- **User Dialogue Transcript Input:** ~150 tokens
- **Output JSON Payload:** ~50 tokens
- **Total Parser Tokens / Claim:** **~400 tokens**

### VLM Image Analyzer Call (`meta-llama/llama-4-scout-17b-16e-instruct`)
- **Prompt Instructions & Taxonomy Maps:** ~800 tokens
- **Image Token Overhead:** Under standard VLM setups, Groq models allocate **~2,048 tokens per image** for processing.
- **Output JSON Payload:** ~100 tokens
- **Total Vision Tokens / Call (1.66 images avg):** 800 + (1.66 * 2048) + 100 = **~4,300 tokens**

---

## 3. Projected Token Totals

| Phase / Dataset | Parser Tokens (LLM) | Vision Tokens (VLM) | Total Tokens |
| :--- | :--- | :--- | :--- |
| **a) sample_claims.csv** (20 rows) | 8,000 | 86,000 | **94,000** |
| **b) claims.csv** (45 rows) | 18,000 | 193,500 | **211,500** |
| **Total Pipeline** | **26,000** | **279,500** | **305,500** |

---

## 4. Groq Free-Tier Limit Check

The Groq Free Tier limits are:
- **Tokens Per Minute (TPM):** 30,000 TPM
- **Tokens Per Day (TPD):** 500,000 TPD

### Feasibility Assessment
1. **Can the full sample evaluation complete within available limits?**
   - **Yes, but ONLY with rate-limit retries.**
   - Running all 20 sample rows sequentially consumes approximately **94,000 tokens**. While this is well within the **500,000 TPD** daily limit, rapid execution will exceed the **30,000 TPM** limit after only 5-6 concurrent VLM calls (approx 5 * 4,300 = 21,500 tokens).
   - If other processes or agents have made VLM calls within the last 24 hours, the cumulative TPD limit is quickly exhausted, triggering daily rate limits.

---

## 5. Caching & Mitigation Recommendations

To build a reliable system, we recommend implementing the following mitigation strategies:

1. **Persistent Local Prediction Caching:**
   - Implement a simple file-based JSON cache (e.g. keying by the hash of `user_claim + image_paths`).
   - If the claim has been processed previously and the code has not changed, return the cached result. This reduces token consumption to **0** for consecutive reruns of the evaluation suite.
2. **Batching & Concatenation:**
   - Group text parsing tasks into a single batch call instead of individual requests, since LLM context windows can handle multiple short claims simultaneously.
3. **Alternate Provider Fallback:**
   - Configure a fallback model/provider (e.g. OpenAI's `gpt-4o-mini` or Google's `gemini-1.5-flash`) via the API key environment configurations. If Groq responds with a 429 rate limit error, automatically route the request to the secondary provider.
