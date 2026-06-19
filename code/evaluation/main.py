import os
from utils.logger import get_logger
from utils.csv_loader import load_csv
import config

logger = get_logger("evaluation")

def run_evaluation():
    logger.info("Starting local evaluation on sample claims...")
    try:
        sample_df = load_csv(config.SAMPLE_CLAIMS_CSV)
        logger.info(f"Loaded {len(sample_df)} sample claims.")
    except Exception as e:
        logger.error(f"Error loading sample dataset: {e}")
        return

    logger.info("Evaluation loop skeleton ready.")

if __name__ == "__main__":
    run_evaluation()
