import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_library_formats():
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    
    # We will try the most common model that we know exists
    model = "meta/llama-3.1-70b-instruct"
    
    formats = [
        "https://integrate.api.nvidia.com/v1",
        "https://integrate.api.nvidia.com/v1/",
        "https://ai.api.nvidia.com/v1",
        "https://ai.api.nvidia.com/v1/"
    ]

    for fmt in formats:
        print(f"\n🧪 Testing Format: '{fmt}'")
        try:
            client = OpenAI(base_url=fmt, api_key=api_key)
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role":"user", "content":"hi"}],
                max_tokens=5,
                timeout=10.0
            )
            print(f"✅ SUCCESS: {completion.choices[0].message.content}")
            return fmt # Return the winner
        except Exception as e:
            print(f"❌ FAILED: {str(e)[:60]}")

if __name__ == "__main__":
    winner = test_library_formats()
    if winner:
        print(f"\n🏆 WINNING FORMAT: {winner}")
    else:
        print("\n💀 No library format worked. Standardizing on 'requests' is likely safer.")
