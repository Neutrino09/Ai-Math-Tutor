# 📘 AI Math Tutor – Human-in-the-Loop Agentic-RAG

An AI-powered **Math Tutor Agent** that behaves like a professor — providing **step-by-step solutions**, ensuring **safety with guardrails**, and improving over time with **human-in-the-loop feedback**.

---

## 🚀 Features

* **Agentic-RAG Architecture**

  * Knowledge Base (GSM8K) → primary retrieval
  * Web Search fallback (MCP via Tavily) → extended coverage
* **Input Guardrails** → only allow math-related queries
* **Output Guardrails** → sanitize unsafe or irrelevant responses
* **Human-in-the-Loop Feedback** → 👍 / 👎 ratings improve performance
* **Frontend (React + Vite)** → clean, modern UI for asking questions
* **Backend (FastAPI)** → orchestrates KB, Web, Guardrails, and Feedback
* **Vector Database (Qdrant)** → semantic search for math problems

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, OpenAI API, Tavily MCP, Qdrant
* **Frontend:** React (Vite), Axios, TailwindCSS (custom styling)
* **Database:** Qdrant (VectorDB)
* **Other:** Docker (for Qdrant), dotenv for secrets

---

## ⚙️ Setup Instructions

### 1. Clone Repo

```bash
git clone https://github.com/Neutrino09/Ai-Math-Tutor.git
cd Ai-Math-Tutor
```

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/` with:

```env
AI_GATEWAY_URL=your-cloudflare-ai-gateway-url
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key   # optional for web search
```

Run backend:

```bash
uvicorn app:app --reload
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

Visit → [http://localhost:5173](http://localhost:5173)

---

## 📊 Usage Examples

### KB Query

**Input:** `Solve 2x + 5 = 17`
**Output:**

```
Step 1: Subtract 5 → 2x = 12  
Step 2: Divide by 2 → x = 6  
Final Answer: 6
```

### Web Search Query

**Input:** `Who is Ramanujan?`
**Output:**

```
Srinivasa Ramanujan (1887–1920) was an Indian mathematician known for contributions to number theory, infinite series, and continued fractions...
```

---

## 🔒 Guardrails

* **Input Guardrail:** Only math-related queries pass (keywords + numeric detection).
* **Output Guardrail:** Filters unsafe/off-topic results.

---

## 👩‍🏫 Human-in-the-Loop

* Every answer includes 👍 / 👎 feedback buttons.
* Feedback is logged into `feedback.json` for iterative improvements.

---

## 📈 Future Improvements

* Expand KB with **JEE Bench** for advanced math.
* Integrate **LangGraph** for modular agent orchestration.
* Retrain embeddings using **feedback logs**.
* Add visualization dashboards for educators.

---

## 📸 Screenshots

<img width="1470" height="956" alt="image" src="https://github.com/user-attachments/assets/89a38490-95ad-4238-ac8b-71272aab126a" />


---

### ⭐ If you like this project, don’t forget to star the repo!
