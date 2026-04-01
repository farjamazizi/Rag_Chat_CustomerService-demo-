import { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState("Ask about shipping, returns, sizing, or payments.");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || loading) {
      return;
    }

    setLoading(true);
    setStatus("Searching the docs and drafting an answer...");

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmed,
          history,
        }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Request failed");
      }

      setHistory((current) => [
        ...current,
        {
          question: trimmed,
          answer: payload.answer,
          sources: payload.sources ?? [],
        },
      ]);
      setQuestion("");
      setStatus("Ready for the next question.");
    } catch (error) {
      setStatus(error.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-shell">
      <div className="bg-orb bg-orb-left" />
      <div className="bg-orb bg-orb-right" />

      <main className="app-frame">
        <section className="hero-card">
          <p className="eyebrow">Local RAG Assistant</p>
          <h1>Customer support answers grounded in your policy docs.</h1>
          <p className="hero-copy">
            A React client backed by a Python RAG API and a local Ollama model.
          </p>
          <div className="status-pill">{status}</div>
        </section>

        <section className="chat-card">
          <div className="chat-header">
            <h2>Ask the assistant</h2>
            <span>{history.length} turns</span>
          </div>

          <div className="chat-log">
            {history.length === 0 ? (
              <div className="empty-state">
                Try: "How do I start a return?" or "How long does standard shipping take?"
              </div>
            ) : (
              history.map((turn, index) => (
                <article className="turn-card" key={`${turn.question}-${index}`}>
                  <div className="turn-label">You</div>
                  <p className="turn-question">{turn.question}</p>
                  <div className="turn-label assistant">Assistant</div>
                  <p className="turn-answer">{turn.answer}</p>
                  {turn.sources?.length > 0 && (
                    <div className="source-list">
                      {turn.sources.map((item) => (
                        <span className="source-chip" key={item.source}>
                          {item.source}
                        </span>
                      ))}
                    </div>
                  )}
                </article>
              ))
            )}
          </div>

          <form className="composer" onSubmit={handleSubmit}>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question about refunds, shipping, sizing, security, or care..."
              rows={4}
            />
            <button disabled={loading} type="submit">
              {loading ? "Thinking..." : "Send question"}
            </button>
          </form>
        </section>
      </main>
    </div>
  );
}

export default App;
