import os
import time
from openai import OpenAI
from dotenv import load_dotenv
import httpx

load_dotenv()

def run_benchmark():
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    base_url = "https://integrate.api.nvidia.com/v1"
    
    models = {
        "Llama 3.3 Super": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "Llama 3.1 Nemotron 70B": "nvidia/llama-3.1-nemotron-70b-instruct",
        "Mistral Large 2": "mistralai/mistral-large-2-instruct",
        "Minimax M2.7": "minimaxai/minimax-m2.7"
    }

    results = []

    print("🏎️  REDLINE CULT LLM BENCHMARK 🏁\n")
    print(f"{'Model Name':<20} | {'Time':<8} | {'Status':<10}")
    print("-" * 45)

    for name, model_id in models.items():
        try:
            http_client = httpx.Client(timeout=30.0)
            client = OpenAI(base_url=base_url, api_key=api_key, http_client=http_client)
            
            start_time = time.time()
            completion = client.chat.completions.create(
                model=model_id,
                messages=[{"role":"user", "content":"Generate one 10-word viral video hook for a Ferrari SF90 Stradale."}],
                max_tokens=20
            )
            end_time = time.time()
            
            elapsed = end_time - start_time
            print(f"{name:<20} | {elapsed:>6.2f}s | ✅ SUCCESS")
            results.append((name, elapsed, completion.choices[0].message.content))
        except Exception as e:
            print(f"{name:<20} | {'FAILED':>7} | ❌ {str(e)[:20]}...")

    print("\n📝 Sample Output (Mistral Large 2):")
    for r in results:
        if r[0] == "Mistral Large 2":
            print(f"   > {r[2]}")
            break

if __name__ == "__main__":
    run_benchmark()
