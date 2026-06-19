import os
from utils.logger import get_logger

logger = get_logger("base_model")

class BaseAPIClient:
    def __init__(self, api_key_env_var="OPENAI_API_KEY", base_url_env_var="OPENAI_BASE_URL"):
        self.api_key = os.environ.get(api_key_env_var)
        self.base_url = os.environ.get(base_url_env_var)
        
        # Fallback support
        if not self.api_key:
            # Check OpenRouter / DashScope specific environment flags
            self.api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
            
        if not self.api_key:
            logger.warning(f"API key missing! Searched in: {api_key_env_var}, OPENROUTER_API_KEY, DASHSCOPE_API_KEY")
            
        logger.info(f"API Client initialized. Base URL: {self.base_url or 'Default'}")
