import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loadingUpload, setLoadingUpload] = useState(false);
  const [loadingAnswer, setLoadingAnswer] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      setUploadStatus("Please select a PDF file.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setUploadStatus("");
    setAnswer("");
    setSources([]);
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus("Please select a PDF first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoadingUpload(true);
    setUploadStatus("");
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setUploadStatus(
        `Document processed successfully • ${data.chunks} chunks created`
      );
    } catch (error) {
      setUploadStatus(`Error: ${error.message}`);
    } finally {
      setLoadingUpload(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;

    setLoadingAnswer(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to get an answer.");
      }

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (error) {
      setAnswer(`Error: ${error.message}`);
      setSources([]);
    } finally {
      setLoadingAnswer(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setUploadStatus("");
    setQuestion("");
    setAnswer("");
    setSources([]);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">✦</div>
          <span>DocuMind</span>
        </div>

        <div className="status-pill">
          <span className="status-dot"></span>
          LOCAL AI
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <div className="eyebrow">RAG DOCUMENT INTELLIGENCE</div>

          <h1>
            Ask your documents.
            <br />
            <span>Understand instantly.</span>
          </h1>

          <p className="subtitle">
            Upload a PDF and ask questions using a private, completely local
            Retrieval-Augmented Generation pipeline.
          </p>
        </section>

        {/* UPLOAD DOCUMENT */}

        <section className="card">
          <div className="section-heading">
            <div className="step-number">01</div>

            <div>
              <h2>Upload document</h2>
              <p>Choose a PDF to index and search</p>
            </div>
          </div>

          <label className="upload-area">
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
            />

            <div className="upload-symbol">↑</div>

            {file ? (
              <>
                <strong>{file.name}</strong>

                <span>
                  {(file.size / 1024 / 1024).toFixed(2)} MB • PDF
                </span>
              </>
            ) : (
              <>
                <strong>Choose a PDF document</strong>
                <span>Click to browse your computer</span>
              </>
            )}
          </label>

          <div className="button-row">
            <button
              className="primary-button"
              onClick={handleUpload}
              disabled={loadingUpload}
            >
              {loadingUpload ? "Processing..." : "Process Document"}
            </button>

            {(file || answer) && (
              <button className="secondary-button" onClick={handleReset}>
                Reset
              </button>
            )}
          </div>

          {uploadStatus && (
            <div
              className={`status-message ${
                uploadStatus.startsWith("Error") ? "error" : "success"
              }`}
            >
              {uploadStatus}
            </div>
          )}
        </section>

        {/* ASK QUESTION */}

        <section className="card">
          <div className="section-heading">
            <div className="step-number">02</div>

            <div>
              <h2>Ask a question</h2>
              <p>Query the information inside your document</p>
            </div>
          </div>

          <div className="question-box">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  handleAsk();
                }
              }}
              placeholder="e.g. What projects are mentioned in this resume?"
              rows={4}
            />

            <div className="question-footer">
              <span>
                Press Enter to ask • Shift + Enter for a new line
              </span>

              <button
                className="ask-button"
                onClick={handleAsk}
                disabled={loadingAnswer || !question.trim()}
              >
                {loadingAnswer ? "Thinking..." : "Ask AI →"}
              </button>
            </div>
          </div>
        </section>

        {/* AI ANSWER */}

        {answer && (
          <section className="answer-card">
            <div className="answer-heading">
              <div className="ai-icon">✦</div>

              <div>
                <div className="eyebrow">AI RESPONSE</div>
                <h2>Answer</h2>
              </div>
            </div>

            <div className="answer-content">
              {answer}
            </div>

            {/* SOURCES */}

            {sources.length > 0 && (
              <div className="sources-section">
                <div className="sources-title">
                  <span>📄</span>
                  <span>Sources</span>
                </div>

                <div className="sources-list">
                  {sources.map((source, index) => (
                    <div className="source-item" key={`${source}-${index}`}>
                      <span className="source-icon">PDF</span>
                      <span>{source}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {/* TECHNOLOGIES */}

        <section className="tech-section">
          <p>BUILT WITH</p>

          <div className="tech-list">
            <span>React</span>
            <span>FastAPI</span>
            <span>Sentence Transformers</span>
            <span>ChromaDB</span>
            <span>Ollama</span>
            <span>Qwen2.5</span>
          </div>
        </section>
      </main>

      <footer>
        <span>Private by design • Runs locally on your machine</span>
      </footer>
    </div>
  );
}

export default App;