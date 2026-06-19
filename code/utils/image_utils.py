import os
import base64
from PIL import Image
from utils.logger import get_logger
import config

logger = get_logger("image_utils")

def resolve_image_path(relative_path):
    # Resolve against the dataset directory
    absolute_path = os.path.abspath(os.path.join(config.DATASET_DIR, relative_path))
    if not os.path.exists(absolute_path):
        logger.warning(f"Image not found at: {absolute_path}")
    return absolute_path

def parse_image_paths(paths_string):
    if not paths_string or not isinstance(paths_string, str):
        return []
    # Paths are separated by semicolons
    raw_paths = [p.strip() for p in paths_string.split(";") if p.strip()]
    return [resolve_image_path(p) for p in raw_paths]

def extract_image_id(image_path):
    # Returns filename without extension (e.g., 'img_1')
    basename = os.path.basename(image_path)
    img_id, _ = os.path.splitext(basename)
    return img_id

def encode_image_to_base64(image_path):
    if not os.path.exists(image_path):
        logger.error(f"Cannot encode missing image: {image_path}")
        return None
    try:
        with open(image_path, "rb") as image_file:
            encoded_bytes = base64.b64encode(image_file.read())
            return encoded_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Error base64 encoding image {image_path}: {e}")
        return None

def get_image_metadata(image_path):
    if not os.path.exists(image_path):
        return {"exists": False}
    try:
        with Image.open(image_path) as img:
            return {
                "exists": True,
                "format": img.format,
                "size": img.size,  # (width, height)
                "mode": img.mode
            }
    except Exception as e:
        logger.error(f"Error reading image metadata for {image_path}: {e}")
        return {"exists": True, "error": str(e)}
