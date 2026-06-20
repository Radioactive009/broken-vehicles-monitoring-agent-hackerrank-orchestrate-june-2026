import os
import sys
import pandas as pd
import json
import time
import hashlib
from dotenv import load_dotenv

# Add parent directory to path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger
from utils.csv_loader import load_csv, save_output_csv
from utils.image_utils import parse_image_paths
from pipelines.claim_pipeline import ClaimVerificationPipeline
import config

logger = get_logger("generate_output")

def main():
    logger.info("Starting Claim Verification System execution on claims.csv...")
    load_dotenv()

    # 1. Load Data
    try:
        claims_df = load_csv(config.CLAIMS_CSV)
    except Exception as e:
        logger.error(f"Error loading inputs: {e}")
        sys.exit(1)

    logger.info(f"Loaded {len(claims_df)} test claims.")

    # 2. Initialize Pipeline
    pipeline = ClaimVerificationPipeline()

    results = []

    # Counters
    total_processed = 0
    total_completed = 0
    used_cache = 0
    used_fallback = 0

    # Wrap call_vlm to detect exceptions
    original_call_vlm = pipeline.analyzer.vlm_client.call_vlm
    fallback_triggered = False

    def wrapper_call_vlm(*args, **kwargs):
        nonlocal fallback_triggered
        try:
            return original_call_vlm(*args, **kwargs)
        except Exception as e:
            fallback_triggered = True
            logger.error(f"Wrapper caught Groq VLM API error: {e}")
            raise e

    pipeline.analyzer.vlm_client.call_vlm = wrapper_call_vlm

    # 3. Pipeline Processing Loop
    for idx, row in claims_df.iterrows():
        user_id = row["user_id"]
        user_claim = row["user_claim"]
        claim_object = row["claim_object"]
        image_paths_raw = row["image_paths"]

        total_processed += 1
        fallback_triggered = False

        # Check parser cache status
        claim_hash = hashlib.sha256(user_claim.encode("utf-8")).hexdigest()
        parser_cached = claim_hash in pipeline.parser.cache

        # Check image analyzer cache status
        image_paths = parse_image_paths(image_paths_raw)
        paths_key = ";".join(sorted(image_paths)) + claim_object
        image_hash_key = hashlib.sha256(paths_key.encode("utf-8")).hexdigest()
        image_cached = image_hash_key in pipeline.analyzer.cache

        is_cached = parser_cached and image_cached

        logger.info(f"Processing row {idx+1}/{len(claims_df)} (User: {user_id}, Object: {claim_object})")
        logger.info(f"Cache status - Parser: {parser_cached}, Image: {image_cached}")

        # Run pipeline with try-except to ensure we never crash
        try:
            out = pipeline.process_claim(user_id, user_claim, claim_object, image_paths_raw)
            total_completed += 1
        except Exception as e:
            logger.error(f"Pipeline crashed on row {idx+1}: {e}. Generating default/fallback outputs.")
            fallback_triggered = True
            # Build mock output
            out = {
                "parsed_claim": {
                    "claimed_issue_type": "unknown",
                    "claimed_object_part": "unknown",
                    "claimed_object": claim_object,
                    "severity_hint": "medium",
                    "confidence": 0.5
                },
                "analysis": {
                    "detected_object": claim_object,
                    "visible_issue_type": "unknown",
                    "visible_object_part": "unknown",
                    "damage_visible": False,
                    "severity": "unknown",
                    "image_quality": "clear",
                    "risk_flags": [],
                    "supporting_image_ids": []
                },
                "validation": {
                    "evidence_standard_met": False,
                    "evidence_standard_met_reason": "VLM analysis failed.",
                    "valid_image": False
                },
                "risks": {
                    "risk_flags": ["manual_review_required"]
                },
                "decision": {
                    "claim_status": "not_enough_information",
                    "claim_status_justification": "System processing failure.",
                    "supporting_image_ids": "none",
                    "severity": "unknown"
                }
            }
            total_completed += 1

        # Track stats
        if is_cached:
            used_cache += 1
            logger.info("Row processed entirely from cache.")
        elif fallback_triggered:
            used_fallback += 1
            logger.info("Row processed using VLM API fallback.")
        else:
            logger.info("Row processed using live API call successfully.")

        decision = out["decision"]
        risks = out["risks"]

        # Gather final output fields required by the challenge
        results.append({
            "user_id": user_id,
            "image_paths": image_paths_raw,
            "user_claim": user_claim,
            "claim_object": claim_object,
            "evidence_standard_met": str(out["validation"]["evidence_standard_met"]).lower(),
            "evidence_standard_met_reason": out["validation"]["evidence_standard_met_reason"],
            "risk_flags": ";".join(risks["risk_flags"]) if risks["risk_flags"] else "none",
            "issue_type": out["analysis"]["visible_issue_type"],
            "object_part": out["analysis"]["visible_object_part"],
            "claim_status": decision["claim_status"],
            "claim_status_justification": decision["claim_status_justification"],
            "supporting_image_ids": decision["supporting_image_ids"],
            "valid_image": str(out["validation"]["valid_image"]).lower(),
            "severity": decision["severity"]
        })

        # Sleep to avoid rate limits if it was a live call
        if not is_cached and not fallback_triggered:
            logger.info("Sleeping for 6 seconds to respect rate limits...")
            time.sleep(6)

    # 4. Save Predictions in Exact Format & Order
    output_df = pd.DataFrame(results)
    
    # Ensure columns order is exactly matching the requirement
    required_cols = [
        "user_id",
        "image_paths",
        "user_claim",
        "claim_object",
        "evidence_standard_met",
        "evidence_standard_met_reason",
        "risk_flags",
        "issue_type",
        "object_part",
        "claim_status",
        "claim_status_justification",
        "supporting_image_ids",
        "valid_image",
        "severity"
    ]
    output_df = output_df[required_cols]
    
    save_output_csv(output_df, config.OUTPUT_CSV)
    logger.info(f"Execution finished. Output saved to {config.OUTPUT_CSV}")

    # Print summary report
    print("\n" + "="*40)
    print("      TEST SET PROCESSING REPORT")
    print("="*40)
    print(f"Rows Processed : {total_processed}")
    print(f"Rows Completed : {total_completed}")
    print(f"Rows using Cache: {used_cache}")
    print(f"Rows using Fallback: {used_fallback}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
