from openai import OpenAI
from typing import Dict, Any, Optional
import json
import httpx
from .base import LLMProvider

class NVIDIAProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "minimaxai/minimax-m2.7"):
        self.api_key = api_key.strip() if api_key else ""
        self.model_name = model_name.strip() if model_name else ""
        
        # Using a custom HTTP client to handle timeouts and robust connectivity
        self.http_client = httpx.Client(timeout=30.0)
        
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key,
            http_client=self.http_client
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
                top_p=0.95,
                max_tokens=2048,
                stream=False
            )

            raw_text = completion.choices[0].message.content
            
            # Simple heuristic for JSON parsing
            parsed_data = None
            if "{" in raw_text and "}" in raw_text:
                try:
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
                    "id": completion.id,
                    "usage": {
                        "prompt_tokens": completion.usage.prompt_tokens,
                        "completion_tokens": completion.usage.completion_tokens,
                        "total_tokens": completion.usage.total_tokens
                    } if hasattr(completion, 'usage') else {}
                }
            }
        except Exception as e:
            raise Exception(f"NVIDIA Library Error: {str(e)}")

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None):
        """Generator that yields text chunks for real-time streaming in UI."""
        
        # 1. Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # 2. Strategy Selection: Always use requests for Llama 3.3 Super (Verified stable)
        force_requests = "llama-3.3-nemotron-super-49b" in self.model_name.lower()
        
        if not force_requests:
            try:
                # Try Library First
                stream = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2048,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return # If successful, exit
            except Exception:
                # Fallback to requests if library fails
                pass

        # 3. Requests Fallback (or forced for Llama 3.3)
        import requests
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": True
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60, stream=True)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_content = line_str[6:]
                            if data_content == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data_content)
                                content = chunk['choices'][0]['delta'].get('content', '')
                                if content:
                                    yield content
                            except:
                                continue
            else:
                raise Exception(f"NVIDIA API Error: {response.status_code}")
        except Exception as e:
            raise Exception(f"Streaming Error: {str(e)}")
