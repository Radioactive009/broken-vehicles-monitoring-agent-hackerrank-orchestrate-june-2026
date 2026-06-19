import os
from utils.logger import get_logger
import config

logger = get_logger("decision_engine")

class DecisionEngine:
    def __init__(self):
        logger.info("Initializing Decision Engine...")

    def make_decision(self, claim_object, parsed_claim, analyzer_output, validator_output, risk_engine_output):
        """
        Synthesizes final status, image-grounded justification, supporting image IDs,
        and severity for the claim verification output.
        """
        evidence_standard_met = validator_output.get("evidence_standard_met", True)
        risk_flags = risk_engine_output.get("risk_flags", [])
        
        detected_object = analyzer_output.get("detected_object", "unknown")
        visible_issue = analyzer_output.get("visible_issue_type", "unknown")
        visible_part = analyzer_output.get("visible_object_part", "unknown")
        damage_visible = analyzer_output.get("damage_visible", False)
        supporting_ids = analyzer_output.get("supporting_image_ids", [])
        severity_raw = analyzer_output.get("severity", "unknown")
        
        claimed_part = parsed_claim.get("claimed_object_part", "unknown")
        claimed_issue = parsed_claim.get("claimed_issue_type", "unknown")
        
        # 1. Map Severity
        severity = severity_raw.lower().strip()
        if severity not in config.SEVERITY_LEVELS:
            severity = "unknown"
            
        # 2. Map Supporting Images
        supporting_image_ids = "none"
        if supporting_ids:
            supporting_image_ids = ";".join(supporting_ids)
            
        # 3. Decision Tree Logic
        claim_status = "not_enough_information"
        justification = ""
        
        # Rule 1: If evidence standard is not met
        if not evidence_standard_met:
            claim_status = "not_enough_information"
            justification = validator_output.get(
                "evidence_standard_met_reason",
                "Insufficient evidence to evaluate the claim."
            )
            # Make sure we clean up default supporting images if standard not met
            supporting_image_ids = "none"
            
        # Rule 2: If evidence is sufficient
        else:
            # check contradiction flags
            if "wrong_object" in risk_flags:
                claim_status = "contradicted"
                justification = f"Claim contradicts image evidence. The detected object is a {detected_object}, which does not match the claimed {claim_object}."
                
            elif "wrong_object_part" in risk_flags:
                claim_status = "contradicted"
                justification = f"Claim contradicts image evidence. Visible damage is on the {visible_part}, which does not match the claimed {claimed_part}."
                
            elif visible_issue == "none" or not damage_visible or "damage_not_visible" in risk_flags:
                claim_status = "contradicted"
                justification = f"Claim contradicts image evidence. The claimed {claimed_part} is visible but appears to have no damage."
                
            elif visible_issue != "unknown" and claimed_issue != "unknown" and visible_issue != claimed_issue:
                claim_status = "contradicted"
                justification = f"Claim contradicts image evidence. The VLM detected {visible_issue} on the {visible_part}, which contradicts the claimed {claimed_issue}."
                
            # check support condition
            elif detected_object == claim_object and visible_part == claimed_part and damage_visible:
                claim_status = "supported"
                justification = f"Claim supported by image evidence. A visible {visible_issue} is present on the {claimed_part}."
                
            # default fallback
            else:
                claim_status = "not_enough_information"
                justification = "Submitted images do not clearly show the claimed issue type on the relevant part."

        return {
            "claim_status": claim_status,
            "claim_status_justification": justification,
            "supporting_image_ids": supporting_image_ids,
            "severity": severity
        }
