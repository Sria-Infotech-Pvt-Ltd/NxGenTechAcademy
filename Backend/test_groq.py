import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not api_key:
    raise RuntimeError("GROQ_API_KEY was not loaded from .env")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "You are testing the NxGen Tech Academy chatbot connection.",
        },
        {
            "role": "user",
            "content": "Reply with exactly: Groq connection successful",
        },
    ],
)

print(response.choices[0].message.content)