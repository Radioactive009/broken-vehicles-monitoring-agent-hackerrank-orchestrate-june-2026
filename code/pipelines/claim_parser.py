import os
import json
import re
from openai import OpenAI
from utils.logger import get_logger
import config

logger = get_logger("claim_parser")

class ClaimParser:
    def __init__(self):
        # Initialize client based on available environment variables
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL")
        
        self.client = None
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://openrouter.ai/api/v1"
            )
        self.model_name = os.environ.get("LLM_MODEL_NAME", "gpt-4o-mini")
        logger.info(f"ClaimParser initialized. API Client available: {self.client is not None}")

    def parse_claim(self, user_claim, claim_object):
        logger.info(f"Parsing claim for object '{claim_object}'...")
        
        # 1. Attempt LLM-based extraction if API key is present
        if self.client:
            try:
                extracted = self._call_llm_parser(user_claim, claim_object)
                if extracted:
                    normalized = self._normalize_extracted_fields(extracted, claim_object)
                    logger.info(f"LLM parsing succeeded: {normalized}")
                    return normalized
            except Exception as e:
                logger.error(f"LLM parsing failed, falling back to rule-based: {e}")
                
        # 2. Fallback to rule-based extraction
        fallback = self._rule_based_parser(user_claim, claim_object)
        logger.info(f"Rule-based fallback result: {fallback}")
        return fallback

    def _call_llm_parser(self, user_claim, claim_object):
        import time
        import re

        # Load prompt template from prompts directory
        prompt_path = os.path.join(config.ROOT_DIR, "prompts", "claim_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
        else:
            prompt_template = "Parse claim conversation: {transcript}\nObject: {claim_object}"

        prompt = prompt_template.format(transcript=user_claim, claim_object=claim_object)
        
        max_retries = 5
        base_delay = 5

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a precise claims processing assistant. You always respond in raw JSON format matching the schema requested."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0
                )
                content = response.choices[0].message.content
                logger.debug(f"Raw LLM response: {content}")
                return json.loads(content)
            except Exception as e:
                err_msg = str(e)
                logger.warning(f"ClaimParser LLM attempt {attempt+1} failed with error: {err_msg}")
                is_rate_limit = "429" in err_msg or "rate_limit" in err_msg.lower() or "rate limit" in err_msg.lower()
                
                if is_rate_limit and attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    match_s = re.search(r"try again in (\d+\.?\d*)s", err_msg)
                    match_m = re.search(r"try again in (\d+)m(\d+\.?\d*)s", err_msg)
                    if match_m:
                        minutes = int(match_m.group(1))
                        seconds = float(match_m.group(2))
                        wait_time = minutes * 60 + seconds + 2
                    elif match_s:
                        wait_time = float(match_s.group(1)) + 2
                    
                    logger.warning(f"Rate limit reached in ClaimParser. Sleeping for {wait_time:.2f}s before retrying...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Error calling LLM Parser API: {e}")
                    raise e

    def _normalize_extracted_fields(self, extracted_dict, claim_object):
        # Normalizes VLM/LLM output fields to the exact taxonomies in config.py
        claimed_part = extracted_dict.get("object_part", "unknown").lower().strip().replace(" ", "_")
        claimed_issue = extracted_dict.get("issue_type", "unknown").lower().strip().replace(" ", "_")
        
        # Resolve synonym mappings programmatically
        claimed_part = self._map_part_synonyms(claimed_part, claim_object)
        claimed_issue = self._map_issue_synonyms(claimed_issue)
        
        # Apply object aware constraint mappings
        claimed_part, claimed_issue = self._apply_object_aware_constraints(claimed_part, claimed_issue, claim_object)
        
        # Strict validation check
        allowed_parts = self._get_allowed_parts(claim_object)
        if claimed_part not in allowed_parts:
            claimed_part = "unknown"
            
        if claimed_issue not in config.ISSUE_TYPE_CATEGORIES:
            claimed_issue = "unknown"
            
        return {
            "claimed_issue_type": claimed_issue,
            "claimed_object_part": claimed_part,
            "claimed_object": claim_object,
            "severity_hint": extracted_dict.get("severity_hint", "medium"),
            "confidence": float(extracted_dict.get("confidence", 0.9))
        }

    def _get_allowed_parts(self, claim_object):
        if claim_object == "car":
            return config.CAR_PARTS
        elif claim_object == "laptop":
            return config.LAPTOP_PARTS
        elif claim_object == "package":
            return config.PACKAGE_PARTS
        return []

    def _map_part_synonyms(self, part, claim_object):
        # Map common verbal descriptors or code-switched phrases
        part = part.replace("pantalla", "screen").replace("teclas", "keyboard")
        part = part.replace("parachoques", "bumper").replace("espejo", "mirror")
        
        # Word boundaries mapping
        if "bumper" in part:
            if "back" in part or "rear" in part:
                return "rear_bumper"
            return "front_bumper"
        if "screen" in part or "display" in part or "glass" in part:
            if claim_object == "car":
                return "windshield"
            return "screen"
        if "keyboard" in part or "key" in part:
            return "keyboard"
        if "trackpad" in part or "mouse" in part or "touchpad" in part:
            return "trackpad"
        if "mirror" in part:
            return "side_mirror"
        if "hinge" in part:
            return "hinge"
        if "lid" in part or "outer" in part:
            return "lid"
        if "corner" in part:
            if claim_object == "package":
                return "package_corner"
            return "corner"
        if "side" in part:
            if claim_object == "package":
                return "package_side"
        if "seal" in part or "tape" in part:
            return "seal"
        if "label" in part or "sticker" in part:
            return "label"
        if "contents" in part or "inside" in part or "product" in part:
            return "contents"
        return part

    def _map_issue_synonyms(self, issue):
        issue_lower = issue.lower().strip()
        if issue_lower in ["scratch", "scrape", "scratched", "scraped", "mark"]:
            return "scratch"
        if issue_lower in ["dent", "bump", "crease", "dented", "creased"]:
            return "dent"
        if issue_lower in ["crack", "cracked", "shattered", "shatter", "glass_shatter"]:
            return "crack"
        if issue_lower in ["broken", "broken_part", "damaged", "broke"]:
            return "broken_part"
        if issue_lower in ["missing", "lost", "missing_part"]:
            return "missing_part"
        if issue_lower in ["torn", "torn_packaging", "open", "opened"]:
            return "torn_packaging"
        if issue_lower in ["crushed", "crushed_packaging"]:
            return "crushed_packaging"
        if issue_lower in ["water", "wet", "water_damage", "spill"]:
            return "water_damage"
        if issue_lower in ["stain", "dirty", "stained", "oil"]:
            return "stain"
            
        if "torn" in issue_lower:
            return "torn_packaging"
        if "crushed" in issue_lower:
            return "crushed_packaging"
        if "water" in issue_lower or "wet" in issue_lower or "spill" in issue_lower:
            return "water_damage"
        if "stain" in issue_lower or "dirty" in issue_lower or "oil" in issue_lower:
            return "stain"
        if "crack" in issue_lower or "shatter" in issue_lower:
            return "crack"
        if "dent" in issue_lower or "bump" in issue_lower:
            return "dent"
        if "scratch" in issue_lower or "scrape" in issue_lower:
            return "scratch"
        if "missing" in issue_lower:
            return "missing_part"
        if "broken" in issue_lower or "damage" in issue_lower:
            return "broken_part"
            
        return issue_lower

    def _apply_object_aware_constraints(self, part, issue, claim_object):
        # Enforce strict part domains
        if claim_object == "car":
            if part in ["screen", "keyboard", "trackpad", "lid", "corner", "base", "port"]:
                part = "unknown"
            elif part in ["box", "package_corner", "package_side", "seal", "label", "contents", "item"]:
                part = "unknown"
        elif claim_object == "laptop":
            if part in ["front_bumper", "rear_bumper", "hood", "windshield", "side_mirror", "headlight", "taillight", "fender", "quarter_panel"]:
                part = "body"
            elif part in ["box", "package_corner", "package_side", "seal", "label", "contents", "item"]:
                part = "body"
        elif claim_object == "package":
            if part in ["front_bumper", "rear_bumper", "door", "hood", "windshield", "side_mirror", "headlight", "taillight", "fender", "quarter_panel"]:
                part = "box"
            elif part in ["screen", "keyboard", "trackpad", "hinge", "lid", "corner", "port", "base"]:
                part = "contents"
                
        # Enforce strict issue domains
        if claim_object == "car":
            if issue in ["torn_packaging", "crushed_packaging"]:
                issue = "dent"
            elif issue in ["water_damage", "stain"]:
                issue = "scratch"  # Map to closest possible visual issue
        elif claim_object == "laptop":
            if issue in ["torn_packaging", "crushed_packaging"]:
                issue = "dent"
        elif claim_object == "package":
            if issue == "dent":
                issue = "crushed_packaging"
            elif issue in ["scratch", "crack", "glass_shatter"]:
                issue = "torn_packaging"
                
        return part, issue

    def _rule_based_parser(self, text, claim_object):
        text = text.lower()
        
        # 1. Determine issue type using regex keywords
        detected_issue = "unknown"
        if re.search(r"dent|bump|creased|crush", text):
            detected_issue = "dent"
        if re.search(r"scratch|scrape|mark", text):
            detected_issue = "scratch"
        if re.search(r"crack|shatter", text):
            detected_issue = "crack"
        if re.search(r"broken|broke|damage", text):
            detected_issue = "broken_part"
        if re.search(r"missing|lost|not inside|not there", text):
            detected_issue = "missing_part"
        if re.search(r"torn|opened", text):
            detected_issue = "torn_packaging"
        if re.search(r"wet|water|spill|stain|oily|oil", text):
            detected_issue = "water_damage"
            
        # Object-specific issue overrides
        if claim_object == "laptop" and "opened" in text and not re.search(r"torn|rip|cut", text):
            # "laptop opened" is normal mechanical function, not torn packaging
            detected_issue = "broken_part" if "broken" in text else "unknown"
            
        # 2. Determine part using regex keywords
        detected_part = "unknown"
        
        # Specific search order based on object type
        if claim_object == "car":
            if "windshield" in text or "glass" in text:
                detected_part = "windshield"
            elif "side mirror" in text or "mirror" in text:
                detected_part = "side_mirror"
            elif "headlight" in text or "front light" in text:
                detected_part = "headlight"
            elif "taillight" in text or "back light" in text or "rear light" in text:
                detected_part = "taillight"
            elif "bumper" in text:
                detected_part = "rear_bumper" if "back" in text or "rear" in text else "front_bumper"
            elif "door" in text:
                detected_part = "door"
            elif "hood" in text:
                detected_part = "hood"
            elif "fender" in text:
                detected_part = "fender"
            elif "quarter panel" in text:
                detected_part = "quarter_panel"
            else:
                detected_part = "body"
        elif claim_object == "laptop":
            if "screen" in text or "display" in text or "glass" in text:
                detected_part = "screen"
            elif "keyboard" in text or "key" in text or "keys" in text or "button" in text:
                detected_part = "keyboard"
            elif "trackpad" in text or "touchpad" in text or "mouse" in text:
                detected_part = "trackpad"
            elif "hinge" in text:
                detected_part = "hinge"
            elif "lid" in text or "cover" in text:
                detected_part = "lid"
            elif "corner" in text:
                detected_part = "corner"
            elif "port" in text or "plug" in text:
                detected_part = "port"
            elif "base" in text or "bottom" in text:
                detected_part = "base"
            else:
                detected_part = "body"
        elif claim_object == "package":
            if "corner" in text:
                detected_part = "package_corner"
            elif "seal" in text or "tape" in text or "flap" in text or "open" in text:
                detected_part = "seal"
            elif "label" in text or "sticker" in text or "address" in text:
                detected_part = "label"
            elif "inside" in text or "item" in text or "product" in text or "contents" in text or "content" in text:
                detected_part = "contents"
            elif "side" in text:
                detected_part = "package_side"
            else:
                detected_part = "box"

        # Refined normalization mapping
        detected_part = self._map_part_synonyms(detected_part, claim_object)
        detected_issue = self._map_issue_synonyms(detected_issue)
        
        # Apply object aware constraints
        detected_part, detected_issue = self._apply_object_aware_constraints(detected_part, detected_issue, claim_object)

        return {
            "claimed_issue_type": detected_issue,
            "claimed_object_part": detected_part,
            "claimed_object": claim_object,
            "severity_hint": "medium",
            "confidence": 0.7
        }
