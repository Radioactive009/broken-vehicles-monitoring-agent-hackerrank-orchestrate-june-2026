import os
from openai import OpenAI
from models.base import BaseAPIClient
from utils.logger import get_logger

logger = get_logger("groq_client")

class GroqVisionClient(BaseAPIClient):
    def __init__(self):
        # We can pass custom env var names to BaseAPIClient or override init
        super().__init__(api_key_env_var="GROQ_API_KEY", base_url_env_var="GROQ_BASE_URL")
        
        # If GROQ_API_KEY is not in the environment via base, let's double check
        if not self.api_key:
            self.api_key = os.environ.get("GROQ_API_KEY")
            
        # Configure client connection
        self.client = None
        self.base_url = self.base_url or "https://api.groq.com/openai/v1"
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            logger.warning("GROQ_API_KEY not found in environment. GroqVisionClient initialized without a client.")
            
        self.model_name = os.environ.get("GROQ_MODEL_NAME", "meta-llama/llama-4-scout-17b-16e-instruct")
        logger.info(f"Groq Vision client set up to use model: {self.model_name} at URL: {self.base_url}")

    def call_vlm(self, prompt, base64_images=None, max_tokens=1024, json_mode=False):
        if not self.client:
            logger.error("API client not initialized. Cannot perform VLM request.")
            raise RuntimeError("API client is uninitialized. Verify GROQ_API_KEY in environment.")
            
        messages = []
        user_content = []
        
        # Add base64 images if present
        if base64_images:
            for b64 in base64_images:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64}"
                    }
                })
            
        # Add prompt text
        user_content.append({
            "type": "text",
            "text": prompt
        })
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        try:
            logger.info(f"Submitting request to Groq VLM ({len(base64_images) if base64_images else 0} images)")
            extra_params = {}
            if json_mode:
                extra_params["response_format"] = {"type": "json_object"}
                
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                **extra_params
            )
            logger.info("Successfully received VLM response from Groq.")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq VLM API: {e}")
            raise e
