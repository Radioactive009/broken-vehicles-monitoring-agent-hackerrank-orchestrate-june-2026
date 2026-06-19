import os
import sys
# Add parent directory to path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from utils.csv_loader import load_csv
from pipelines.claim_parser import ClaimParser
import config

logger = get_logger("evaluation_parser")

def run_claim_parser_test():
    logger.info("Initializing Claim Parser evaluation...")
    parser = ClaimParser()

    try:
        sample_df = load_csv(config.SAMPLE_CLAIMS_CSV)
    except Exception as e:
        logger.error(f"Failed to load sample dataset: {e}")
        return

    logger.info(f"Running claim parser on {len(sample_df)} sample rows...")
    
    success_count = 0
    total = len(sample_df)

    for idx, row in sample_df.iterrows():
        user_claim = row["user_claim"]
        claim_object = row["claim_object"]
        
        # Expected outputs from the sample dataset
        expected_part = row["object_part"]
        # Wait, since the expected output column 'issue_type' is the visible issue,
        # we can still log the comparison as a reference
        
        result = parser.parse_claim(user_claim, claim_object)
        
        logger.info(f"Row {idx+1} | Object: {claim_object}")
        logger.info(f"  Transcript: {user_claim[:100]}...")
        logger.info(f"  Parser output: Part={result['claimed_object_part']}, Issue={result['claimed_issue_type']}")
        logger.info(f"  Expected visible in sample: Part={expected_part}, Issue={row['issue_type']}")
        logger.info("-" * 40)
        success_count += 1

    logger.info(f"Completed processing {success_count}/{total} cases.")

if __name__ == "__main__":
    run_claim_parser_test()
