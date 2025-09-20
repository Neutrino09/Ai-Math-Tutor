import os
import traceback
import json
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from qdrant_client import QdrantClient
from openai import OpenAI
from tavily import TavilyClient

# --- Load environment ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

# --- Clients ---
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("AI_GATEWAY_URL")
)

qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "math_kb"

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

# --- FastAPI app ---
app = FastAPI()

# ✅ CORS wide open for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class QueryRequest(BaseModel):
    question: str

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    correct: bool

# --- Guardrails ---
def is_math_question(question: str) -> bool:
    math_keywords = [
        "math", "number", "calculate", "solve", "compute", "find", "simplify",
        "add", "sum", "plus", "subtract", "minus", "difference",
        "multiply", "times", "product", "divide", "quotient", "modulo",
        "equation", "linear", "quadratic", "polynomial", "factor", "variable",
        "expression", "root", "square root", "cube root",
        "derivative", "differentiate", "integral", "limit", "function",
        "geometry", "triangle", "circle", "radius", "diameter", "area",
        "perimeter", "volume", "angle", "trigonometry", "sine", "cosine", "tan",
        "probability", "statistics", "mean", "median", "mode", "variance",
        "standard deviation", "distribution", "random", "combinatorics",
        "permutation", "combination", "binomial",
        "matrix", "vector", "determinant", "eigenvalue", "prime"
    ]
    q_lower = question.lower()

    # Allow if any math keyword appears
    if any(kw in q_lower for kw in math_keywords):
        return True

    # Allow if the question has numbers (e.g., "2 + 2", "Tom has 5 apples")
    if re.search(r"\d", q_lower):
        return True

    return False

def sanitize_output(answer: str) -> str:
    banned = ["kill", "hack", "attack", "nsfw", "violence"]
    for word in banned:
        if word in answer.lower():
            return "❌ Output blocked: unsafe content detected."
    return answer

# --- Helpers ---
def get_embedding(text: str):
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding

def search_kb(question: str, threshold: float = 0.75):
    vec = get_embedding(question)
    res = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=vec,
        limit=3,
        with_payload=True,
        with_vectors=False
    )
    if not res.points:
        return None, None
    best = res.points[0]
    if best.score is None or best.score < threshold:
        return None, best.score
    return best.payload, best.score

def search_web(question: str):
    if not tavily:
        return {"answer": "Web search disabled (missing TAVILY_API_KEY in backend/.env)."}
    res = tavily.search(query=question, max_results=3)
    if not res or "results" not in res:
        return {"answer": "No results found on the web."}
    snippets = [r.get("content", "").strip() for r in res["results"] if r.get("content")]
    return {"answer": "Web search results:\n" + "\n".join(snippets)}

# --- Routes ---
@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: QueryRequest):
    try:
        # 🚧 Input Guardrail
        if not is_math_question(req.question):
            return {"error": "❌ Only math-related questions are allowed."}

        kb_payload, score = search_kb(req.question)
        if kb_payload:
            solution = sanitize_output(kb_payload["solution"])  # 🚧 Output Guardrail
            return {
                "source": "KB",
                "score": score,
                "question": kb_payload["question"],
                "solution": solution
            }
        web = search_web(req.question)
        web["answer"] = sanitize_output(web["answer"])  # 🚧 Output Guardrail
        return {"source": "Web", **web}
    except Exception as e:
        print("ERROR in /ask:\n", traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": f"{type(e).__name__}: {str(e)}"})

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    feedback_file = Path(__file__).resolve().parent / "feedback.json"

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": req.question,
        "answer": req.answer,
        "correct": req.correct,
    }

    if feedback_file.exists():
        with open(feedback_file, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(feedback_file, "w") as f:
        json.dump(data, f, indent=2)

    print("📝 Feedback recorded:", entry)
    return {"status": "ok", "message": "Feedback recorded."}
