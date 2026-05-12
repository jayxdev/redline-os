import requests
import json
from typing import Dict, Any, Optional
from .base import LLMProvider

class NVIDIAProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "meta/llama-3-70b-instruct"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://integrate.api.nvidia.com/v1/chat/completions"

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.5,
            "top_p": 1,
            "max_tokens": 1024,
            "stream": False
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            raw_text = data["choices"][0]["message"]["content"]
            
            # Simple heuristic for JSON parsing if the prompt expects it
            parsed_data = None
            if "{" in raw_text and "}" in raw_text:
                try:
                    # Find potential JSON block
                    start = raw_text.find("{")
                    end = raw_text.rfind("}") + 1
                    json_str = raw_text[start:end]
                    parsed_data = json.loads(json_str)
                except:
                    pass

            return {
                "raw_text": raw_text,
                "parsed_data": parsed_data,
                "model_name": self.model_name,
                "provider_name": "nvidia",
                "metadata": {
                    "usage": data.get("usage", {}),
                    "id": data.get("id")
                }
            }
        except Exception as e:
            raise Exception(f"NVIDIA API Error: {str(e)}")
