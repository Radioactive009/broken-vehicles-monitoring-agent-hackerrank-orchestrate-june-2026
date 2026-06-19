# Claim Verification System

This system implements a production-grade multi-modal pipeline to verify visual damage claims for Cars, Laptops, and Packages using submitted images, conversation transcripts, and user historical logs.

## Architecture Overview

The system is structured as a modular processing pipeline:
1. **Claim Parser**: Extracts target object parts and issue types from conversation transcripts using text-based LLMs.
2. **User Context Evaluator**: Looks up historical flags and requirements to formulate minimum evidence benchmarks.
3. **VLM Vision Analyzer**: Runs visual checks on the images to identify part visibility, damage types, image quality defects, and adversarial text injection.
4. **Decision Engine**: Combines NLP and visual findings using deterministic rules to issue the final claim status (`supported`, `contradicted`, `not_enough_information`), severity, and risk flags.
5. **Output Schema Guard**: Ensures all predictions map strictly to allowed taxonomies and schema formats.

## Setup Instructions

1. Install dependencies from the `code/` directory:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure API credentials. Set one or more of the following environment variables:
   - `OPENAI_API_KEY` for GPT models
   - `GEMINI_API_KEY` for Google Gemini models

## Execution Instructions

To run the pipeline and generate predictions for the test set (`dataset/claims.csv`):
```bash
python main.py
```
This will output the final predictions to the project root directory as `output.csv`.

## Evaluation Instructions

To run the local evaluation script and assess performance metrics on the labeled sample dataset (`dataset/sample_claims.csv`):
```bash
python evaluation/main.py
```
This will print metric scores (Accuracy, F1) to the console and update `evaluation/evaluation_report.md` with operational latency, cost, and rate-limiting considerations.
