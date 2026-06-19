import os
import pandas as pd
from utils.logger import get_logger
import config

logger = get_logger("evidence_validator")

class EvidenceValidator:
    def __init__(self):
        logger.info("Initializing Evidence Validator...")
        self.requirements_path = config.EVIDENCE_REQUIREMENTS_CSV
        self.requirements_df = None
        self._load_requirements()

    def _load_requirements(self):
        if os.path.exists(self.requirements_path):
            try:
                self.requirements_df = pd.read_csv(self.requirements_path)
                logger.info(f"Loaded {len(self.requirements_df)} evidence requirements.")
            except Exception as e:
                logger.error(f"Error loading evidence requirements CSV: {e}")
        else:
            logger.warning(f"Requirements file not found at {self.requirements_path}")

    def get_requirement_for_claim(self, claim_object, parsed_claim_data):
        """
        Determines the matched requirement_id and description from evidence_requirements.csv
        based on the claim object and issue family.
        """
        issue_type = parsed_claim_data.get("claimed_issue_type", "unknown")
        object_part = parsed_claim_data.get("claimed_object_part", "unknown")
        
        req_id = "REQ_GENERAL_OBJECT_PART"
        
        if claim_object == "car":
            if issue_type in ["dent", "scratch"]:
                req_id = "REQ_CAR_BODY_PANEL"
            elif issue_type in ["crack", "glass_shatter", "broken_part", "missing_part"]:
                req_id = "REQ_CAR_GLASS_LIGHT_MIRROR"
            else:
                req_id = "REQ_CAR_IDENTITY_OR_SIDE"
        elif claim_object == "laptop":
            if object_part in ["screen", "keyboard", "trackpad"]:
                req_id = "REQ_LAPTOP_SCREEN_KEYBOARD_TRACKPAD"
            elif object_part in ["hinge", "lid", "corner", "body", "base", "port"]:
                req_id = "REQ_LAPTOP_BODY_HINGE_PORT"
        elif claim_object == "package":
            if issue_type in ["crushed_packaging", "torn_packaging"] or object_part == "seal":
                req_id = "REQ_PACKAGE_EXTERIOR"
            elif issue_type in ["water_damage", "stain"] or object_part == "label":
                req_id = "REQ_PACKAGE_LABEL_OR_STAIN"
            elif object_part in ["contents", "item"]:
                req_id = "REQ_PACKAGE_CONTENTS"
                
        # Look up description in dataframe if loaded
        description = ""
        if self.requirements_df is not None:
            matches = self.requirements_df[self.requirements_df["requirement_id"] == req_id]
            if not matches.empty:
                description = matches.iloc[0]["minimum_image_evidence"]
                
        return req_id, description

    def validate_evidence(self, claim_object, parsed_claim_data, analyzer_output):
        """
        Determines evidence_standard_met, evidence_standard_met_reason, and valid_image
        based on image analyzer outputs and the matched evidence requirements.
        """
        # 1. Match requirement
        req_id, req_desc = self.get_requirement_for_claim(claim_object, parsed_claim_data)
        logger.info(f"Matched claim to requirement: {req_id}")
        
        # Extract analyzer fields
        risk_flags = analyzer_output.get("risk_flags", [])
        damage_visible = analyzer_output.get("damage_visible", False)
        visible_part = analyzer_output.get("visible_object_part", "unknown")
        detected_object = analyzer_output.get("detected_object", "unknown")
        
        claimed_part = parsed_claim_data.get("claimed_object_part", "unknown")
        claimed_issue = parsed_claim_data.get("claimed_issue_type", "unknown")
        
        # 2. Determine valid_image
        valid_image = True
        
        # Images are invalid if they are non-original (stock/web images)
        if "non_original_image" in risk_flags:
            valid_image = False
            
        # Images are invalid if severe blur/obstruction prevents checking anything and no damage is seen
        if "blurry_image" in risk_flags and "damage_not_visible" in risk_flags:
            valid_image = False
            
        if "cropped_or_obstructed" in risk_flags and "damage_not_visible" in risk_flags:
            valid_image = False

        # 3. Determine evidence_standard_met
        evidence_standard_met = True
        reasons = []
        
        # Mismatches automatically fail standard sufficiency
        if "wrong_object" in risk_flags:
            evidence_standard_met = False
            reasons.append("The submitted image does not show the correct object type.")
            
        if "wrong_object_part" in risk_flags:
            evidence_standard_met = False
            reasons.append(f"The visible damage is on a different part than the claimed {claimed_part}.")
            
        if "wrong_angle" in risk_flags and "damage_not_visible" in risk_flags:
            evidence_standard_met = False
            reasons.append("The image angle is incorrect and prevents inspection of the claimed damage.")
            
        if not valid_image and "damage_not_visible" in risk_flags:
            evidence_standard_met = False
            reasons.append("The image quality is insufficient (too blurry, cropped, or non-original) to verify the claim.")
            
        # If part is not visible at all
        if "damage_not_visible" in risk_flags and visible_part == "unknown" and claimed_part != "unknown":
            evidence_standard_met = False
            reasons.append(f"The claimed part ({claimed_part}) is not visible in the image.")

        # 4. Generate reason text
        if evidence_standard_met:
            # Construct a positive reasoning sentence grounded in the matched requirement context
            if claim_object == "car":
                evidence_standard_met_reason = f"The {claimed_part} is visible and the claimed condition can be evaluated."
            elif claim_object == "laptop":
                evidence_standard_met_reason = f"The laptop {claimed_part} area is visible clearly enough to inspect."
            else:
                evidence_standard_met_reason = f"The package {claimed_part} is visible clearly enough to inspect."
        else:
            evidence_standard_met_reason = " ".join(reasons)
            
        return {
            "evidence_standard_met": evidence_standard_met,
            "evidence_standard_met_reason": evidence_standard_met_reason,
            "valid_image": valid_image
        }
