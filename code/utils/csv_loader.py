import os
import pandas as pd
from utils.logger import get_logger

logger = get_logger("csv_loader")

def load_csv(file_path):
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    logger.info(f"Loading CSV file from: {file_path}")
    return pd.read_csv(file_path)

def load_user_history(file_path):
    df = load_csv(file_path)
    # Return user_id to history dict for quick local O(1) lookup
    return df.set_index("user_id").to_dict(orient="index")

def load_evidence_requirements(file_path):
    df = load_csv(file_path)
    # Store requirements under keys
    requirements = {}
    for _, row in df.iterrows():
        key = (row["claim_object"], row["applies_to"])
        requirements[key] = row["minimum_image_evidence"]
    return requirements

def save_output_csv(output_df, file_path):
    logger.info(f"Saving predictions CSV to: {file_path}")
    output_df.to_csv(file_path, index=False)
    logger.info("Save complete.")
