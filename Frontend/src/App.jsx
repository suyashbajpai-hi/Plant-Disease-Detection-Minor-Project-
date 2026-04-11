import { useEffect, useMemo, useState } from "react";

const CROP_OPTIONS = [
  { value: "cotton", label: "🌿 Cotton" },
  { value: "wheat", label: "🌾 Wheat" },
];

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

function formatConfidence(value) {
  return `${(value * 100).toFixed(2)}%`;
}

function severityLevel(confidence) {
  if (confidence >= 0.9) return { label: "High Confidence", color: "#22763a" };
  if (confidence >= 0.7) return { label: "Moderate Confidence", color: "#b8860b" };
  return { label: "Low Confidence", color: "#9b1f1f" };
}

export default function App() {
  const [crop, setCrop] = useState("cotton");
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!file) {
      setPreviewUrl("");
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const endpoint = useMemo(() => `${API_BASE_URL}/predict/${crop}`, [crop]);

  async function handlePredict(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("Please upload a plant leaf image first.");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${endpoint}?top_k=5`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || "Prediction failed. Please try again.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Could not connect to API.");
    } finally {
      setLoading(false);
    }
  }

  const severity = result ? severityLevel(result.confidence) : null;
  const isHealthy = result?.predicted_class?.toLowerCase().includes("healthy");

  return (
    <div className="page">
      <div className="background-grid" aria-hidden="true" />
      <main className="app-shell">
        <section className="hero">
          <p className="eyebrow">AI Crop Diagnostic</p>
          <h1>Plant Disease Detection</h1>
          <p>
            Upload a clear leaf photo and choose the crop model. The system predicts the disease
            class and confidence in seconds.
          </p>
        </section>

        <section className="panel">
          <form className="predict-form" onSubmit={handlePredict}>
            <label htmlFor="crop">Select Crop Model</label>
            <select
              id="crop"
              value={crop}
              onChange={(e) => {
                setCrop(e.target.value);
                setResult(null);
                setError("");
              }}
            >
              {CROP_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <label htmlFor="file">Upload Leaf Image</label>
            <input
              id="file"
              type="file"
              accept="image/*"
              onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setResult(null);
                setError("");
              }}
            />
            <p className="input-hint">
              Only cotton or wheat plant leaf images are accepted. Other images are rejected.
            </p>

            <button type="submit" disabled={loading}>
              {loading ? "Analyzing..." : "Predict Disease"}
            </button>
          </form>

          <div className="preview-card">
            <h2>Image Preview</h2>
            {previewUrl ? (
              <img src={previewUrl} alt="Uploaded leaf preview" />
            ) : (
              <div className="empty-preview">No image selected</div>
            )}
          </div>
        </section>

        {(result || error) && (
          <section className="result-panel">
            {error && <p className="error-text">{error}</p>}

            {result && (
              <>
                {/* Primary diagnosis */}
                <div className="diagnosis-card">
                  <div className="diagnosis-header">
                    <span className={`status-badge ${isHealthy ? "healthy" : "disease"}`}>
                      {isHealthy ? "✓ Healthy" : "⚠ Disease Detected"}
                    </span>
                    <span className="crop-badge">{result.crop}</span>
                  </div>

                  <h2 className="disease-name">{result.predicted_class}</h2>
                  {result.scientific_name && (
                    <p className="scientific-name">{result.scientific_name}</p>
                  )}

                  <div className="confidence-section">
                    <div className="confidence-header">
                      <span>Confidence</span>
                      <strong style={{ color: severity.color }}>{formatConfidence(result.confidence)}</strong>
                    </div>
                    <div className="confidence-bar-track">
                      <div
                        className="confidence-bar-fill"
                        style={{
                          width: `${(result.confidence * 100).toFixed(1)}%`,
                          backgroundColor: severity.color
                        }}
                      />
                    </div>
                    <span className="severity-label" style={{ color: severity.color }}>
                      {severity.label}
                    </span>
                  </div>
                </div>




              </>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
