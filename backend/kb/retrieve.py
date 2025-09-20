import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from openai import OpenAI

# Load .env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

print("DEBUG: AI_GATEWAY_URL =", os.getenv("AI_GATEWAY_URL"))
print("DEBUG: OPENAI_API_KEY =", (os.getenv("OPENAI_API_KEY") or "")[:12] + "...")

# OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("AI_GATEWAY_URL")
)

# Qdrant client
qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "math_kb"

# Embedding helper
def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# Query
query = "Add 2 and 2 together"
query_vector = get_embedding(query)

results = qdrant.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=1
)

print("\n🔎 Query:", query)
print("✅ Retrieved:", results.points[0].payload)
