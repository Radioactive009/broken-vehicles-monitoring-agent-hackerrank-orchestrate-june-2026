import os
import pandas as pd
from utils.logger import get_logger
from utils.csv_loader import load_csv, load_user_history, load_evidence_requirements, save_output_csv
import config

logger = get_logger("main")

def main():
    logger.info("Starting Claim Verification System execution...")
    
    # 1. Load Data
    try:
        claims_df = load_csv(config.CLAIMS_CSV)
        user_history = load_user_history(config.USER_HISTORY_CSV)
        requirements = load_evidence_requirements(config.EVIDENCE_REQUIREMENTS_CSV)
    except Exception as e:
        logger.error(f"Error loading inputs: {e}")
        return

    logger.info(f"Loaded {len(claims_df)} test claims.")
    
    # 2. Pipeline Processing Loop
    # (To be implemented: running claim_pipeline on each row)
    
    logger.info("Execution finished. Output generation is currently pending implementation.")

if __name__ == "__main__":
    main()
