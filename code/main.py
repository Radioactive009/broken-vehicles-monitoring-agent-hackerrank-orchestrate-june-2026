import os
import sys
import pandas as pd
import time
from dotenv import load_dotenv

# Add parent directory to path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger
from utils.csv_loader import load_csv, save_output_csv
from pipelines.claim_pipeline import ClaimVerificationPipeline
import config

logger = get_logger("main")

def main():
    logger.info("Starting Claim Verification System execution...")
    load_dotenv()

    # Verify GROQ API KEY
    if not os.environ.get("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY environment variable is not set.")
        sys.exit(1)

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

    # 3. Pipeline Processing Loop
    for idx, row in claims_df.iterrows():
        claim_id = row.get("claim_id", f"claim_{idx+1}")
        user_id = row["user_id"]
        user_claim = row["user_claim"]
        claim_object = row["claim_object"]
        image_paths_raw = row["image_paths"]

        logger.info(f"Processing row {idx+1}/{len(claims_df)} (Claim: {claim_id}, Object: {claim_object})")

        # Run pipeline
        out = pipeline.process_claim(user_id, user_claim, claim_object, image_paths_raw)

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
            "risk_flags": ";".join(risks["risk_flags"]),
            "issue_type": out["analysis"]["visible_issue_type"],
            "object_part": out["analysis"]["visible_object_part"],
            "claim_status": decision["claim_status"],
            "claim_status_justification": decision["claim_status_justification"],
            "supporting_image_ids": decision["supporting_image_ids"],
            "valid_image": str(out["validation"]["valid_image"]).lower(),
            "severity": decision["severity"]
        })

        # Add a sleep to prevent 429 TPM Rate Limits on Groq free tier
        time.sleep(6)

    # 4. Save Predictions
    output_df = pd.DataFrame(results)
    save_output_csv(output_df, config.OUTPUT_CSV)
    logger.info(f"Execution finished. Output saved to {config.OUTPUT_CSV}")

if __name__ == "__main__":
    main()
