import os
from openai import OpenAI
from dotenv import load_dotenv

# Load env
load_dotenv()

def test_nvidia():
    api_key = os.getenv("NVIDIA_API_KEY")
    model = os.getenv("DEFAULT_LLM_MODEL", "meta/llama-3-70b-instruct")
    
    if not api_key or "nvapi" not in api_key:
        print("❌ Error: NVIDIA_API_KEY is missing or invalid.")
        return

    print(f"📡 Connecting to NVIDIA API with model: {model}...")
    
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":"Hello, respond with 'NVIDIA Connection Successful' if you can read this."}],
            temperature=0.5,
            top_p=1,
            max_tokens=1024,
            stream=False
        )
        
        response = completion.choices[0].message.content
        print(f"✅ Response Received: {response}")
        
    except Exception as e:
        print(f"❌ API Call Failed: {str(e)}")

if __name__ == "__main__":
    test_nvidia()
