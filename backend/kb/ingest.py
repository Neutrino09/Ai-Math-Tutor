import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI

# --- Load .env safely ---
# Look in parent folder (project root) or backend folder
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # fallback, current dir

# Debug prints
print("DEBUG: .env loaded from ->", env_path if env_path.exists() else "current folder")
print("DEBUG: AI_GATEWAY_URL =", os.getenv("AI_GATEWAY_URL"))
print("DEBUG: OPENAI_API_KEY =", (os.getenv("OPENAI_API_KEY") or "")[:12] + "...")

# --- OpenAI client via Cloudflare Gateway ---
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("AI_GATEWAY_URL")
)

# --- Qdrant client ---
qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "math_kb"

# --- Sample math problem ---
data = {
    "id": 1,
    "question": "What is 2 + 2?",
    "solution": "Step 1: Add 2 and 2 → 4. Final Answer: 4."
}

# --- Get real embedding ---
def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

embedding = get_embedding(data["question"])

# --- Recreate collection (size = 1536 for embedding) ---
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
)

# --- Insert into Qdrant ---
qdrant.upsert(
    collection_name=COLLECTION_NAME,
    points=[
        models.PointStruct(
            id=data["id"],
            vector=embedding,
            payload=data
        )
    ]
)

print("✅ Ingested one math problem with real embedding")
