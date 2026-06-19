import os
import sys
import pandas as pd
import json
import time
from dotenv import load_dotenv

# Add parent directory to path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from utils.csv_loader import load_csv
from utils.image_utils import parse_image_paths
from pipelines.claim_parser import ClaimParser
from pipelines.image_analyzer import ImageAnalyzer
from pipelines.evidence_validator import EvidenceValidator
from pipelines.risk_engine import RiskEngine
from pipelines.decision_engine import DecisionEngine
from pipelines.claim_pipeline import ClaimVerificationPipeline
import config

logger = get_logger("evaluation_main")

def run_full_evaluation():
    logger.info("Initializing complete evaluation pipeline...")
    load_dotenv()
    
    # Check GROQ API KEY
    if not os.environ.get("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY environment variable is not set.")
        sys.exit(1)
        
    try:
        sample_df = load_csv(config.SAMPLE_CLAIMS_CSV)
    except Exception as e:
        logger.error(f"Failed to load sample dataset: {e}")
        sys.exit(1)
        
    logger.info(f"Loaded {len(sample_df)} sample claims.")
    
    # Initialize components
    pipeline = ClaimVerificationPipeline()
    
    results = []
    
    # Accuracy counters
    metrics = {
        "claim_status": 0,
        "issue_type": 0,
        "object_part": 0,
        "severity": 0,
        "evidence_standard_met": 0,
        "valid_image": 0
    }
    
    for idx, row in sample_df.iterrows():
        user_id = row["user_id"]
        user_claim = row["user_claim"]
        claim_object = row["claim_object"]
        image_paths_raw = row["image_paths"]
        
        logger.info(f"Processing row {idx+1}/{len(sample_df)} (User: {user_id}, Object: {claim_object})")
        
        # Run standard pipeline
        out = pipeline.process_claim(user_id, user_claim, claim_object, image_paths_raw, mock_idx=idx)
        
        parsed_claim_data = {
            "claimed_object_part": out["parsed_claim"].get("claimed_object_part", "unknown"),
            "claimed_issue_type": out["parsed_claim"].get("claimed_issue_type", "unknown")
        }
        analysis = out["analysis"]
        validation = out["validation"]
        risks = out["risks"]
        decision = out["decision"]
        
        # Compile outputs
        pred_status = decision["claim_status"]
        pred_issue = analysis["visible_issue_type"]
        pred_part = analysis["visible_object_part"]
        pred_severity = decision["severity"]
        pred_standard = validation["evidence_standard_met"]
        pred_valid = validation["valid_image"]
        
        expected_status = row["claim_status"]
        expected_issue = row["issue_type"]
        expected_part = row["object_part"]
        expected_severity = row["severity"]
        expected_standard = bool(row["evidence_standard_met"])
        expected_valid = bool(row["valid_image"])
        
        # Check correctness
        if pred_status == expected_status:
            metrics["claim_status"] += 1
        # Handle taxonomy synonym comparisons for issues in parser/VLM accuracy
        if pred_issue == expected_issue or pipeline.decision_engine.issue_similarity(pred_issue, expected_issue) in ["exact_match", "compatible"]:
            metrics["issue_type"] += 1
        if pred_part == expected_part or pipeline.decision_engine.part_similarity(pred_part, expected_part):
            metrics["object_part"] += 1
        if pred_severity == expected_severity:
            metrics["severity"] += 1
        if pred_standard == expected_standard:
            metrics["evidence_standard_met"] += 1
        if pred_valid == expected_valid:
            metrics["valid_image"] += 1
            
        results.append({
            "idx": idx,
            "user_id": user_id,
            "image_paths": image_paths_raw,
            "user_claim": user_claim,
            "claim_object": claim_object,
            "evidence_standard_met_expected": expected_standard,
            "evidence_standard_met_predicted": pred_standard,
            "evidence_standard_met_reason": validation["evidence_standard_met_reason"],
            "risk_flags": ";".join(risks["risk_flags"]),
            "issue_type_expected": expected_issue,
            "issue_type_predicted": pred_issue,
            "object_part_expected": expected_part,
            "object_part_predicted": pred_part,
            "claim_status_expected": expected_status,
            "claim_status_predicted": pred_status,
            "claim_status_justification": decision["claim_status_justification"],
            "supporting_image_ids": decision["supporting_image_ids"],
            "valid_image_expected": expected_valid,
            "valid_image_predicted": pred_valid,
            "severity_expected": expected_severity,
            "severity_predicted": pred_severity
        })
        
        # Add a sleep to prevent 429 TPM Rate Limits on Groq free tier
        time.sleep(6)

    # Print results to stdout
    total = len(sample_df)
    print("\n" + "="*50)
    print("           EVALUATION PIPELINE METRICS")
    print("="*50)
    for k, val in metrics.items():
        acc = (val / total) * 100
        print(f"{k.replace('_', ' ').capitalize():<30} : {acc:.1f}% ({val}/{total})")
    print("="*50 + "\n")
    
    # Save predictions CSV
    predictions_df = pd.DataFrame(results)
    csv_out_path = os.path.join(config.ROOT_DIR, "evaluation", "sample_predictions.csv")
    predictions_df.to_csv(csv_out_path, index=False)
    logger.info(f"Saved sample predictions to {csv_out_path}")
    
    # Save evaluation report markdown
    report_path = os.path.join(config.ROOT_DIR, "evaluation", "evaluation_report.md")
    
    md_content = "# Complete Evaluation Report\n\n"
    md_content += "## Summary Metrics\n"
    md_content += "| Metric | Accuracy (%) | Matches | Total |\n"
    md_content += "| :--- | :--- | :--- | :--- |\n"
    for k, val in metrics.items():
        acc = (val / total) * 100
        label = k.replace('_', ' ').capitalize()
        md_content += f"| {label} | {acc:.1f}% | {val} | {total} |\n"
        
    md_content += "\n## Case by Case Prediction Details\n\n"
    for r in results:
        md_content += f"### Row {r['idx']+1} (User: {r['user_id']}, Object: {r['claim_object'].upper()})\n"
        md_content += f"- **Claim Status:** Expected: `{r['claim_status_expected']}` | Predicted: `{r['claim_status_predicted']}`\n"
        md_content += f"- **Justification:** *\"{r['claim_status_justification']}\"*\n"
        md_content += f"- **Evidence sufficiency:** Expected: `{r['evidence_standard_met_expected']}` | Predicted: `{r['evidence_standard_met_predicted']}`\n"
        md_content += f"- **Image Usability:** Expected: `{r['valid_image_expected']}` | Predicted: `{r['valid_image_predicted']}`\n"
        md_content += f"- **Part Match:** Expected: `{r['object_part_expected']}` | Predicted: `{r['object_part_predicted']}`\n"
        md_content += f"- **Issue Match:** Expected: `{r['issue_type_expected']}` | Predicted: `{r['issue_type_predicted']}`\n\n"
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    logger.info(f"Saved evaluation report to {report_path}")

if __name__ == "__main__":
    run_full_evaluation()
