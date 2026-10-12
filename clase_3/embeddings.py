import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

text = """
Hoy es un buen día. Es Viernes y hace sol.
"""

response = requests.post(
    "https://openrouter.ai/api/v1/embeddings",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-OpenRouter-Title": "Embeddings PoC", # Optional. Site title for rankings on openrouter.ai.
    },
    json={
        "model": "openai/text-embedding-3-small",
        "input": text,
        "dimensions": 1536
    }
)
response.raise_for_status()
embedding = response.json()["data"][0]["embedding"]

print(embedding)
