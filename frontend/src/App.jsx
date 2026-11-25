
import { useState } from "react";
import "./App.css";

function App() {
  const [description, setDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyseTicket(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/tickets/analyse",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ description }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Failed to analyse ticket"
        );
      }

      setResult(data.classification);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <header>
        <h1>TicketAI</h1>
        <p>Intelligent IT Support Assistant</p>
      </header>

      <form onSubmit={analyseTicket}>
        <label htmlFor="description">
          Support Ticket Description
        </label>

        <textarea
          id="description"
          placeholder="Describe your technical issue..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={5000}
          required
        />

        <button disabled={loading || !description.trim()}>
          {loading ? "Analysing ticket..." : "Analyse Ticket"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <section className="result">
          <h2>Classification Result</h2>

          <div className="classification-grid">
            <div>
              <span>Category</span>
              <strong>{result.category}</strong>
            </div>

            <div>
              <span>Priority</span>
              <strong
                className={`priority ${result.priority.toLowerCase()}`}
              >
                {result.priority}
              </strong>
            </div>

            <div>
              <span>Assigned Team</span>
              <strong>{result.team}</strong>
            </div>
          </div>

          <h3>Issue Summary</h3>
          <p>{result.summary}</p>

          <h3>Suggested Response</h3>
          <p>{result.suggested_response}</p>

          <small>AI-generated result. Human review recommended.</small>
        </section>
      )}
    </main>
  );
}

export default App;
