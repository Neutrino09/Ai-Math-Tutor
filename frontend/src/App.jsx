import React, { useState } from "react";
import axios from "axios";
import "./index.css";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async () => {
    setLoading(true);
    setError("");
    setResponse(null);
    try {
      const res = await axios.post(
        `${API_BASE}/ask`,
        { question },
        { headers: { "Content-Type": "application/json" } }
      );
      setResponse(res.data);
    } catch (err) {
      const msg =
        err?.response?.data?.error ||
        err?.message ||
        "Something went wrong. Check backend logs.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const sendFeedback = async (correct) => {
    try {
      await axios.post(`${API_BASE}/feedback`, {
        question,
        answer: JSON.stringify(response),
        correct,
      });
      alert("Thanks for your feedback!");
    } catch (err) {
      console.error("Feedback error:", err);
    }
  };

  return (
    <div className="page">
      <header className="header">
        <h1 className="title">Math Tutor</h1>
      </header>

      <main className="container">
        <div className="card">
          <textarea
            rows="3"
            className="input"
            placeholder="Ask me a math question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button
            className="btn"
            onClick={askQuestion}
            disabled={loading || !question.trim()}
          >
            {loading ? "Thinking…" : "Ask"}
          </button>

          {error && <div className="error">{error}</div>}

          {response && (
            <div className="answer-box">
              <h2>Answer</h2>
              {response.source === "KB" ? (
                <>
                  <p className="source">Source: Knowledge Base</p>
                  <p><b>Question:</b> {response.question}</p>
                  <pre className="solution">{response.solution}</pre>
                </>
              ) : (
                <>
                  <p className="source">Source: Web</p>
                  <ul>
                    {response.answer
                      .split("\n")
                      .filter((line) => line.trim() !== "")
                      .map((line, i) => (
                        <li key={i}>{line}</li>
                      ))}
                  </ul>
                </>
              )}

              {/* Feedback Section */}
              <div className="feedback">
                <span>Was this helpful?</span>
                <button
                  className="feedback-btn"
                  onClick={() => sendFeedback(true)}
                >
                  👍
                </button>
                <button
                  className="feedback-btn"
                  onClick={() => sendFeedback(false)}
                >
                  👎
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
