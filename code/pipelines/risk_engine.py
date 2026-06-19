import os
import pandas as pd
from utils.logger import get_logger
import config

logger = get_logger("risk_engine")

class RiskEngine:
    def __init__(self):
        logger.info("Initializing Risk Engine...")
        self.history_path = config.USER_HISTORY_CSV
        self.history_df = None
        self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_path):
            try:
                self.history_df = pd.read_csv(self.history_path)
                logger.info(f"Loaded {len(self.history_df)} user history profiles.")
            except Exception as e:
                logger.error(f"Error loading user history CSV: {e}")
        else:
            logger.warning(f"User history file not found at {self.history_path}")

    def get_user_profile(self, user_id):
        if self.history_df is not None:
            matches = self.history_df[self.history_df["user_id"] == user_id]
            if not matches.empty:
                return matches.iloc[0].to_dict()
        return None

    def evaluate_risk(self, user_id, parsed_claim, analyzer_output, validator_output):
        """
        Evaluates user profile history risks and merges them with VLM image-level risks,
        determining the final set of risk_flags.
        """
        risk_flags = set()
        
        # 1. Fetch user history profile
        profile = self.get_user_profile(user_id)
        has_history_risk = False
        escalate_manual = False
        
        if profile:
            past_claims = int(profile.get("past_claim_count", 0))
            rejected = int(profile.get("rejected_claim", 0))
            manual_review = int(profile.get("manual_review_claim", 0))
            last_90_days = int(profile.get("last_90_days_claim_count", 0))
            history_flags_raw = str(profile.get("history_flags", "none")).lower()
            
            # Historic flags
            if "user_history_risk" in history_flags_raw:
                has_history_risk = True
            if "manual_review_required" in history_flags_raw:
                escalate_manual = True
                
            # Exceeding reasonable thresholds rules
            if rejected >= 2:
                has_history_risk = True
            if last_90_days >= 3:
                has_history_risk = True
            if past_claims >= 10:
                has_history_risk = True
                
            # Escalations
            if rejected >= 3:
                escalate_manual = True
        else:
            logger.warning(f"No user history found for user: {user_id}. Defaulting to standard risk rules.")
            
        if has_history_risk:
            risk_flags.add("user_history_risk")

        # 2. Merge image-level risks from Analyzer
        image_risks = analyzer_output.get("risk_flags", [])
        for flag in image_risks:
            if flag in config.RISK_FLAGS_CATEGORIES and flag != "none":
                risk_flags.add(flag)

        # 3. Apply claim mismatch mapping
        # "claim_mismatch" is added if there is any mismatch in object, part, or visible damage
        if any(f in risk_flags for f in ["wrong_object", "wrong_object_part", "damage_not_visible"]):
            risk_flags.add("claim_mismatch")

        # 4. Manual review requirement rules
        # - Prompt injection escalates immediately
        if "text_instruction_present" in risk_flags:
            escalate_manual = True
            
        # - Multiple concurrent image-level risk factors (e.g. blurry + wrong angle)
        if len([r for r in image_risks if r in ["blurry_image", "cropped_or_obstructed", "low_light_or_glare", "wrong_angle"]]) >= 2:
            escalate_manual = True
            
        # - High rejection history combined with any visual risk
        if profile and int(profile.get("rejected_claim", 0)) >= 1 and len(image_risks) >= 1:
            escalate_manual = True
            
        # - Mismatches and history risk combined
        if ("wrong_object" in risk_flags or "wrong_object_part" in risk_flags) and has_history_risk:
            escalate_manual = True
            
        # - Evidence sufficiency issues
        if not validator_output.get("evidence_standard_met", True) or not validator_output.get("valid_image", True):
            escalate_manual = True
            
        if escalate_manual:
            risk_flags.add("manual_review_required")

        # Clean list output
        final_flags = [f for f in config.RISK_FLAGS_CATEGORIES if f in risk_flags]
        if not final_flags:
            final_flags = ["none"]
            
        return {
            "risk_flags": final_flags
        }
