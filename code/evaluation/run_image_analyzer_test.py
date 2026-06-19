import os
import sys
import pandas as pd
import json
from dotenv import load_dotenv

# Ensure code/ is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.claim_parser import ClaimParser
from pipelines.image_analyzer import ImageAnalyzer
from utils.image_utils import parse_image_paths

def test_analyzer():
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable is not set.")
        sys.exit(1)
        
    # Read sample claims
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_csv = os.path.abspath(os.path.join(script_dir, "..", "..", "dataset", "sample_claims.csv"))
    
    if not os.path.exists(sample_csv):
        print(f"Error: sample_claims.csv not found at {sample_csv}")
        sys.exit(1)
        
    df = pd.read_csv(sample_csv)
    
    # 5 selected test indices: 0 (car), 1 (car - wrong_object/mismatch), 8 (laptop), 9 (laptop), 14 (package)
    test_indices = [0, 1, 8, 9, 14]
    
    parser = ClaimParser()
    analyzer = ImageAnalyzer()
    
    test_results = []
    
    for idx in test_indices:
        row = df.iloc[idx]
        user_claim = row["user_claim"]
        claim_object = row["claim_object"]
        image_paths_raw = row["image_paths"]
        
        # 1. Parse Claim Text
        print(f"\n--- [Case {idx}] Parsing Claim ({claim_object}) ---")
        parsed_claim = parser.parse_claim(user_claim, claim_object)
        
        # Translate keys for the VLM's context
        parsed_claim_data = {
            "claimed_object_part": parsed_claim.get("claimed_object_part", "unknown"),
            "claimed_issue_type": parsed_claim.get("claimed_issue_type", "unknown")
        }
        print(f"Parsed Claim Data: {parsed_claim_data}")
        
        # 2. Get absolute image paths
        # Note: raw paths in CSV are like 'images/sample/case_001/img_1.jpg'
        # The parse_image_paths function resolves them against the dataset directory
        image_paths = parse_image_paths(image_paths_raw)
        print(f"Image Paths: {image_paths}")
        
        # 3. Analyze Images
        print(f"Analyzing Images for Case {idx}...")
        analysis = analyzer.analyze_images(image_paths, claim_object, parsed_claim_data)
        print(f"Analysis Output: {json.dumps(analysis, indent=2)}")
        
        test_results.append({
            "idx": idx,
            "claim_object": claim_object,
            "user_claim": user_claim,
            "image_paths_raw": image_paths_raw,
            "parsed_claim": parsed_claim_data,
            "analysis": analysis,
            "expected": {
                "issue_type": row.get("issue_type"),
                "object_part": row.get("object_part"),
                "risk_flags": row.get("risk_flags")
            }
        })
        
    # Generate the report
    generate_report(test_results)

def generate_report(results):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(script_dir, "image_analyzer_report.md")
    
    md = "# Production Image Analyzer Evaluation Report\n\n"
    
    md += "## Normalization Mappings\n"
    md += "The `ImageAnalyzer` normalizes raw VLM responses using python-based substring dictionaries:\n\n"
    md += "### Objects\n"
    md += "- `cardboard box`, `shipping box`, `box`, `carton`, `parcel` -> `package`\n"
    md += "- `automobile`, `vehicle`, `sedan`, `suv`, `truck` -> `car`\n"
    md += "- `notebook`, `macbook`, `pc`, `computer` -> `laptop`\n\n"
    md += "### Issues\n"
    md += "- `collision`, `impact damage`, `bumper dent`, `dented` -> `dent`\n"
    md += "- `scrape`, `scuff`, `abrasion` -> `scratch`\n"
    md += "- `fracture`, `split` -> `crack`\n"
    md += "- `shattered glass`, `broken screen`, `shattered screen` -> `glass_shatter`\n"
    md += "- `physical damage`, `crushed`, `crushed corner`, `smashed` -> `crushed_packaging`\n"
    md += "- `torn`, `ripped`, `torn box` -> `torn_packaging`\n"
    md += "- `leak`, `spill` -> `water_damage`\n\n"
    md += "### Parts\n"
    md += "- `trunk bumper`, `back bumper`, `rear bumper and trunk` -> `rear_bumper`\n"
    md += "- `front fascia`, `front bumper area` -> `front_bumper`\n"
    md += "- `display`, `panel`, `lcd` -> `screen`\n"
    md += "- `key`, `keys` -> `keyboard`\n"
    md += "- `track pad`, `mousepad` -> `trackpad`\n"
    md += "- `corner of box`, `box corner` -> `package_corner`\n"
    md += "- `side of box`, `box side` -> `package_side`\n\n"
    
    md += "## Prompts & Schema\n"
    md += "The analyzer uses a strict prompt structure requesting a structured JSON payload with fields:\n"
    md += "- `detected_object`\n"
    md += "- `visible_issue_type`\n"
    md += "- `visible_object_part`\n"
    md += "- `damage_visible`\n"
    md += "- `severity`\n"
    md += "- `image_quality`\n"
    md += "- `risk_flags`\n"
    md += "- `supporting_image_ids`\n\n"
    
    md += "## Example Outputs & Comparisons\n\n"
    
    for r in results:
        md += f"### Case {r['idx']} ({r['claim_object'].upper()})\n"
        md += f"- **Image Paths:** `{r['image_paths_raw']}`\n"
        md += f"- **Expected Ground Truth:**\n"
        md += f"  - Issue Type: `{r['expected']['issue_type']}`\n"
        md += f"  - Object Part: `{r['expected']['object_part']}`\n"
        md += f"  - Expected Risk Flags: `{r['expected']['risk_flags']}`\n"
        
        md += f"- **Image Analyzer Output:**\n"
        md += "```json\n"
        md += json.dumps(r['analysis'], indent=2)
        md += "\n```\n\n"
        
    md += "## Failure Cases and Mitigations\n"
    md += "- **VLM Ambiguities:** When a VLM identifies a general issue (e.g. 'physical damage'), we resolve it to specific taxonomy classes (e.g. 'crushed_packaging') based on the context of the claim object (Cars vs. Laptops vs. Packages).\n"
    md += "- **Implicit Verification:** If the VLM fails to flag mismatches or no damage, our post-processing logic validates object/part agreement programmatically and injects appropriate risk flags (`wrong_object`, `wrong_object_part`, `damage_not_visible`).\n"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)
        
    print(f"Generated report at {report_path}")

if __name__ == "__main__":
    test_analyzer()
