import os
import sys
from dotenv import load_dotenv

# Ensure the root is in path
sys.path.append(os.getcwd())

from redline.providers.llm.nvidia_provider import NVIDIAProvider

def test_live_streaming():
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    model = os.getenv("DEFAULT_LLM_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1").strip()
    
    print(f"📡 Testing Live Streaming...")
    print(f"Model: {model}")
    
    if not api_key:
        print("❌ Error: NVIDIA_API_KEY not found in .env")
        return

    provider = NVIDIAProvider(api_key, model)
    prompt = "Give me a 5-word catchy hook for a car video about drifting."
    
    print("AI Response: ", end="", flush=True)
    try:
        for chunk in provider.generate_stream(prompt):
            print(chunk, end="", flush=True)
        print("\n✅ Streaming Test Passed!")
    except Exception as e:
        print(f"\n❌ Streaming Test Failed: {str(e)}")

if __name__ == "__main__":
    test_live_streaming()
