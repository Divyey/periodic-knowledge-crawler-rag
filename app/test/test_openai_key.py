import os
from dotenv import load_dotenv

load_dotenv()

try:
    import openai
except ImportError:
    print("openai package not installed. Run: pip install openai")
    exit(1)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY not found in .env or environment.")
    exit(1)


try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello!"}]
    )
    print("✅ OpenAI API key is working!")
    print("Sample response:", response.choices[0].message.content.strip())
except Exception as e:
    print("❌ OpenAI API key test failed:", e)
