import os
import sys
import json
from dotenv import load_dotenv

# Ensure the code/ directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.groq_client import GroqVisionClient
from utils.image_utils import encode_image_to_base64
from utils.logger import get_logger

logger = get_logger("test_groq")

def test_text_only(client):
    logger.info("--- Testing Text-Only Call with JSON Mode ---")
    prompt = (
        "Respond with a JSON object containing three fields: 'status' (string, value should be 'success'), "
        "'code' (integer, value should be 200), and 'message' (string, value should be 'Text connectivity test successful')."
    )
    try:
        response_text = client.call_vlm(prompt=prompt, json_mode=True)
        logger.info(f"Raw Text Response:\n{response_text}")
        
        # Verify JSON
        data = json.loads(response_text)
        assert data.get("status") == "success"
        assert data.get("code") == 200
        logger.info("Text-Only JSON verification PASSED!")
        return True
    except Exception as e:
        logger.error(f"Text-Only connectivity test FAILED: {e}")
        return False

def test_multimodal(client):
    logger.info("--- Testing Multimodal Call with JSON Mode ---")
    # Resolve the path to case_001/img_1.jpg
    # Since test_groq.py is in code/, the relative path to dataset is ../dataset/images/sample/case_001/img_1.jpg
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.abspath(os.path.join(script_dir, "..", "dataset", "images", "sample", "case_001", "img_1.jpg"))
    
    if not os.path.exists(image_path):
        logger.error(f"Test image not found at {image_path}. Cannot complete multimodal test.")
        return False
        
    logger.info(f"Encoding test image: {image_path}")
    b64_image = encode_image_to_base64(image_path)
    if not b64_image:
        logger.error("Failed to base64 encode the test image.")
        return False
        
    prompt = (
        "Analyze the provided image. Respond with a JSON object with the following fields: "
        "'detected_object' (string, the object visible in the image, e.g. car, laptop, package, or other), "
        "'damage_visible' (boolean, true if there is any visible damage, false otherwise), "
        "'confidence' (float, between 0.0 and 1.0)."
    )
    
    try:
        response_text = client.call_vlm(prompt=prompt, base64_images=[b64_image], json_mode=True)
        logger.info(f"Raw Multimodal Response:\n{response_text}")
        
        # Verify JSON
        data = json.loads(response_text)
        assert "detected_object" in data
        assert "damage_visible" in data
        assert isinstance(data.get("damage_visible"), bool)
        logger.info("Multimodal JSON verification PASSED!")
        return True
    except Exception as e:
        logger.error(f"Multimodal connectivity test FAILED: {e}")
        return False

def main():
    load_dotenv()
    
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("GROQ_API_KEY is not set in environment or .env file.")
        print("Please set GROQ_API_KEY environment variable before running this test.")
        sys.exit(1)
        
    logger.info("Initializing GroqVisionClient...")
    client = GroqVisionClient()
    
    text_ok = test_text_only(client)
    image_ok = test_multimodal(client)
    
    if text_ok and image_ok:
        logger.info("=== All Groq Integration Tests PASSED ===")
        sys.exit(0)
    else:
        logger.error("=== Some Groq Integration Tests FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
