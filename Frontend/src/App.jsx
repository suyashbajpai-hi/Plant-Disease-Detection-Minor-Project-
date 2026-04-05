import { useEffect, useMemo, useState } from "react";

const CROP_OPTIONS = [
  { value: "cotton", label: "Cotton" },
  { value: "wheat", label: "Wheat" },
];

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

function formatConfidence(value) {
  return `${(value * 100).toFixed(2)}%`;
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

      const response = await fetch(`${endpoint}?top_k=3`, {
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
                <div className="result-headline">
                  <h2>Predicted Disease</h2>
                  <span>{result.predicted_class}</span>
                </div>

                <p className="confidence">Confidence: {formatConfidence(result.confidence)}</p>

                <h3>Top Predictions</h3>
                <ul className="top-k-list">
                  {result.top_k?.map((item) => (
                    <li key={item.class_name}>
                      <span>{item.class_name}</span>
                      <strong>{formatConfidence(item.confidence)}</strong>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
