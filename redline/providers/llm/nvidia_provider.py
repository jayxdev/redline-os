from openai import OpenAI
from typing import Dict, Any, Optional
import json
import httpx
from .base import LLMProvider

class NVIDIAProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "nvidia/llama-3.3-nemotron-super-49b-v1"):
        self.api_key = api_key.strip() if api_key else ""
        self.model_name = model_name.strip() if model_name else ""
        
        # Use the default internal client for maximum compatibility with streaming
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key
        )

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=False
            )
            raw_text = completion.choices[0].message.content
            return {"raw_text": raw_text, "model_name": self.model_name, "parsed_data": None} # Simplified for brevity
        except Exception as e:
            raise Exception(f"NVIDIA Error: {str(e)}")

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None):
        """Generator that yields text chunks for real-time streaming in UI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            # Use the official library streaming - now that httpx is removed, this is stable
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            # Final fallback to requests if the library construction still fails for specific models
            import requests
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model_name, "messages": messages, "stream": True}
            
            try:
                response = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                data_content = line_str[6:]
                                if data_content == '[DONE]': break
                                chunk_json = json.loads(data_content)
                                content = chunk_json['choices'][0]['delta'].get('content', '')
                                if content: yield content
                else:
                    raise Exception(f"NVIDIA API Error: {response.status_code}")
            except:
                raise Exception(f"All connection attempts failed: {str(e)}")
