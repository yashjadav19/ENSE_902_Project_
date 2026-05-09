import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

# Older SDK format - set organization in headers
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    default_headers={"anthropic-org-id": "62f690b4-8f1a-4900-97ba-9eb8795c2d5a"}
)

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key loaded: {bool(api_key)} (length: {len(api_key) if api_key else 0})")

try:
    response = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=10,
        messages=[{"role": "user", "content": "test"}]
    )
    print("✓ Model works!")
except Exception as e:
    print(f"✗ Error: {e}")