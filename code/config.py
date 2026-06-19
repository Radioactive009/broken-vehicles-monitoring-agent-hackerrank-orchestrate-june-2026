import os

# Paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(ROOT_DIR, "..", "dataset")

# CSV File Paths
SAMPLE_CLAIMS_CSV = os.path.join(DATASET_DIR, "sample_claims.csv")
CLAIMS_CSV = os.path.join(DATASET_DIR, "claims.csv")
USER_HISTORY_CSV = os.path.join(DATASET_DIR, "user_history.csv")
EVIDENCE_REQUIREMENTS_CSV = os.path.join(DATASET_DIR, "evidence_requirements.csv")
OUTPUT_CSV = os.path.join(ROOT_DIR, "..", "output.csv")

# Allowed Taxonomy Categories
CLAIM_STATUS_CATEGORIES = ["supported", "contradicted", "not_enough_information"]

ISSUE_TYPE_CATEGORIES = [
    "dent", "scratch", "crack", "glass_shatter", "broken_part",
    "missing_part", "torn_packaging", "crushed_packaging",
    "water_damage", "stain", "none", "unknown"
]

CAR_PARTS = [
    "front_bumper", "rear_bumper", "door", "hood", "windshield",
    "side_mirror", "headlight", "taillight", "fender", "quarter_panel",
    "body", "unknown"
]

LAPTOP_PARTS = [
    "screen", "keyboard", "trackpad", "hinge", "lid", "corner",
    "port", "base", "body", "unknown"
]

PACKAGE_PARTS = [
    "box", "package_corner", "package_side", "seal", "label",
    "contents", "item", "unknown"
]

SEVERITY_LEVELS = ["none", "low", "medium", "high", "unknown"]

RISK_FLAGS_CATEGORIES = [
    "none", "blurry_image", "cropped_or_obstructed", "low_light_or_glare",
    "wrong_angle", "wrong_object", "wrong_object_part", "damage_not_visible",
    "claim_mismatch", "possible_manipulation", "non_original_image",
    "text_instruction_present", "user_history_risk", "manual_review_required"
]
