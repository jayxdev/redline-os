import os
from openai import OpenAI
from dotenv import load_dotenv
import httpx

load_dotenv()

def run_diagnostic():
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    
    gateways = [
        "https://integrate.api.nvidia.com/v1",
        "https://ai.api.nvidia.com/v1"
    ]
    
    # Try the most common standard model first
    models = ["meta/llama-3.1-70b-instruct", "minimaxai/minimax-m2.7"]

    for gw in gateways:
        print(f"\n🌐 Gateway: {gw}")
        # Using a custom client with short timeouts
        http_client = httpx.Client(timeout=10.0)
        client = OpenAI(base_url=gw, api_key=api_key, http_client=http_client)
        
        for model in models:
            try:
                print(f"   🤖 Model: {model}...", end=" ", flush=True)
                client.chat.completions.create(
                    model=model,
                    messages=[{"role":"user", "content":"hi"}],
                    max_tokens=1
                )
                print("✅ WORKING")
                return # FOUND IT
            except Exception as e:
                print(f"❌ {str(e)[:40]}...")

if __name__ == "__main__":
    run_diagnostic()
