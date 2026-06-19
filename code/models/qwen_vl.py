import os
from openai import OpenAI
from models.base import BaseAPIClient
from utils.logger import get_logger

logger = get_logger("qwen_vl")

class QwenVLClient(BaseAPIClient):
    def __init__(self):
        super().__init__(api_key_env_var="OPENAI_API_KEY", base_url_env_var="OPENAI_BASE_URL")
        
        # Configure client connection
        self.client = None
        if self.api_key:
            # We initialize standard OpenAI compatible client
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://openrouter.ai/api/v1"
            )
            
        self.model_name = os.environ.get("QWEN_MODEL_NAME", "qwen/qwen-2.5-vl-3b-instruct")
        logger.info(f"Qwen-VL client set up to use model: {self.model_name}")

    def call_vlm(self, prompt, base64_images, max_tokens=1024, json_mode=False):
        if not self.client:
            logger.error("API client not initialized. Cannot perform VLM request.")
            raise RuntimeError("API client is uninitialized. Verify API keys in environment.")
            
        messages = []
        user_content = []
        
        # Add base64 images to query payload following OpenAI/OpenRouter schema
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
            logger.info(f"Submitting request to Qwen VLM ({len(base64_images)} images)")
            extra_params = {}
            if json_mode:
                extra_params["response_format"] = {"type": "json_object"}
                
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                **extra_params
            )
            logger.info("Successfully received VLM response.")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Qwen VLM API: {e}")
            raise e
