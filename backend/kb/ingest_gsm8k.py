import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from openai import OpenAI
from datasets import load_dataset
import math

# --- Load environment ---
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# --- Clients ---
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("AI_GATEWAY_URL")
)
qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "math_kb"

# --- Load GSM8K dataset ---
print("📥 Loading GSM8K dataset...")
dataset = load_dataset("gsm8k", "main")["train"]

# --- Recreate collection ---
print("🗄️ Creating collection in Qdrant...")
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
)

# --- Parameters ---
N = len(dataset)  # full dataset
BATCH_SIZE = 50   # embed 50 at a time

# --- Helper: embed batch ---
def embed_batch(texts):
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [d.embedding for d in resp.data]

# --- Ingest in batches ---
print(f"⚡ Ingesting ALL {N} GSM8K problems into Qdrant (batch size {BATCH_SIZE})...")

for start in range(0, N, BATCH_SIZE):
    end = min(start + BATCH_SIZE, N)
    batch = dataset.select(range(start, end))

    questions = [item["question"] for item in batch]
    embeddings = embed_batch(questions)

    points = []
    for i, (item, emb) in enumerate(zip(batch, embeddings), start=start):
        points.append(
            models.PointStruct(
                id=i,
                vector=emb,
                payload={
                    "question": item["question"],
                    "solution": item["answer"]
                }
            )
        )

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Ingested {end}/{N} problems")

print(f"🎉 Finished ingesting ALL {N} GSM8K problems into Qdrant")
