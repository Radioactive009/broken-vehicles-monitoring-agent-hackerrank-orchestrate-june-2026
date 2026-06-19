import os
from utils.logger import get_logger
import config

logger = get_logger("decision_engine")

class DecisionEngine:
    def __init__(self):
        logger.info("Initializing Decision Engine...")

    def issue_similarity(self, issue_a, issue_b):
        """
        Compares two issue types to check if they are identical, compatible synonyms, or mismatches.
        """
        a = str(issue_a).lower().replace(" ", "_").strip()
        b = str(issue_b).lower().replace(" ", "_").strip()
        
        if a == b:
            return "exact_match"
            
        compatible_sets = [
            {"crack", "glass_shatter"},
            {"dent", "collision"},
            {"broken_part", "missing_part"},
            {"torn_packaging", "crushed_packaging"},
            {"water_damage", "stain"}
        ]
        
        for cset in compatible_sets:
            if a in cset and b in cset:
                return "compatible"
                
        return "mismatch"

    def part_similarity(self, part_a, part_b):
        """
        Checks if two object parts are compatible.
        """
        a = str(part_a).lower().replace("_", " ").strip()
        b = str(part_b).lower().replace("_", " ").strip()
        
        if a == b:
            return True
            
        # Check display and screen compatibility
        if ("screen" in a or "display" in a or "lcd" in a) and ("screen" in b or "display" in b or "lcd" in b):
            return True
            
        # Check bumper compatibility
        if "bumper" in a and "bumper" in b:
            return True
            
        # Check substring containment
        if a in b or b in a:
            return True
            
        # Side mirror compatibility
        if "mirror" in a and "mirror" in b:
            return True
            
        return False

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
        
        # Check similarity
        issue_match = self.issue_similarity(claimed_issue, visible_issue)
        parts_match = self.part_similarity(claimed_part, visible_part)
        
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
            # check object mismatch
            if "wrong_object" in risk_flags or (detected_object != "other" and detected_object != claim_object):
                claim_status = "contradicted"
                justification = f"Claim contradicts image evidence. The detected object is a {detected_object}, which does not match the claimed {claim_object}."
                
            # check part mismatch (if parts are not compatible)
            elif not parts_match and "wrong_object_part" in risk_flags:
                claim_status = "contradicted"
                justification = f"Claim contradicts image evidence. Visible damage is on the {visible_part}, which does not match the claimed {claimed_part}."
                
            # check undamaged contradiction
            elif visible_issue == "none" or not damage_visible or "damage_not_visible" in risk_flags:
                claim_status = "contradicted"
                justification = f"Claim contradicts image evidence. The claimed {claimed_part} is visible but appears to have no damage."
                
            # check issue contradiction (if issues mismatch completely)
            elif visible_issue != "unknown" and claimed_issue != "unknown" and issue_match == "mismatch":
                claim_status = "contradicted"
                justification = f"Claim contradicts image evidence. The VLM detected {visible_issue} on the {visible_part}, which contradicts the claimed {claimed_issue}."
                
            # check support condition (exact match or compatible issues, and compatible parts)
            elif detected_object == claim_object and parts_match and damage_visible and issue_match in ["exact_match", "compatible"]:
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
