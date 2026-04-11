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

  // LLM detailed recommendation state
  const [farmSize, setFarmSize] = useState("");
  const [llmResult, setLlmResult] = useState(null);
  const [llmError, setLlmError] = useState("");
  const [llmLoading, setLlmLoading] = useState(false);

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

  async function fetchLlmAdvice(predictionData, acres) {
    setLlmError("");
    setLlmResult(null);
    setLlmLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          crop: predictionData.crop,
          disease: predictionData.predicted_class,
          remedies: predictionData.recommendation?.remedies || [],
          farm_size_acres: acres,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || "Failed to get detailed recommendation.");
      }
      setLlmResult(data.detailed_recommendation);
    } catch (err) {
      setLlmError(err.message || "Could not connect to LLM service.");
    } finally {
      setLlmLoading(false);
    }
  }

  async function handlePredict(event) {
    event.preventDefault();
    setError("");
    setResult(null);
    setLlmResult(null);
    setLlmError("");

    if (!file) {
      setError("Please upload a plant leaf image first.");
      return;
    }

    const acres = parseFloat(farmSize);
    if (!farmSize || isNaN(acres) || acres <= 0) {
      setError("Please enter a valid farm size in acres.");
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

      // Auto-trigger LLM advisory for diseased plants
      const healthy = data.predicted_class?.toLowerCase().includes("healthy");
      if (!healthy) {
        fetchLlmAdvice(data, acres);
      }
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
                setLlmResult(null);
                setLlmError("");
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
                setLlmResult(null);
                setLlmError("");
              }}
            />
            <p className="input-hint">
              Only cotton or wheat plant leaf images are accepted. Other images are rejected.
            </p>

            <label htmlFor="farmSize">Farm Size (acres)</label>
            <input
              id="farmSize"
              type="number"
              min="0.1"
              step="0.1"
              placeholder="e.g. 5"
              value={farmSize}
              onChange={(e) => setFarmSize(e.target.value)}
            />

            <button type="submit" disabled={loading || llmLoading}>
              {loading ? "Analyzing..." : llmLoading ? "Generating Report..." : "Predict Disease"}
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

                {/* Detailed AI Advisory (auto-loaded) */}
                {!isHealthy && (
                  <div className="llm-section">
                    <h3>🤖 AI-Powered Detailed Advisory</h3>

                    {llmLoading && (
                      <div className="llm-loading">
                        <div className="spinner" />
                        <p>Generating detailed report for {farmSize} acres...</p>
                      </div>
                    )}

                    {llmError && <p className="error-text">{llmError}</p>}

                    {llmResult && !llmResult.parse_error && (
                      <div className="llm-result">
                        {/* Cause Analysis */}
                        {llmResult.cause_analysis && (
                          <div className="llm-card">
                            <h4>🔬 Why This Disease Occurs</h4>
                            <p>{llmResult.cause_analysis}</p>
                          </div>
                        )}

                        {/* Cure Details */}
                        {llmResult.cure_details?.length > 0 && (
                          <div className="llm-card">
                            <h4>💊 Cure Details</h4>
                            <table className="llm-table">
                              <thead>
                                <tr>
                                  <th>Product</th>
                                  <th>Type</th>
                                  <th>Active Ingredient</th>
                                  <th>Dosage / Acre</th>
                                </tr>
                              </thead>
                              <tbody>
                                {llmResult.cure_details.map((item, i) => (
                                  <tr key={i}>
                                    <td>{item.product_name}</td>
                                    <td><span className="tag">{item.type}</span></td>
                                    <td>{item.active_ingredient}</td>
                                    <td>{item.dosage_per_acre}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}

                        {/* Application Guide */}
                        {llmResult.application_guide?.length > 0 && (
                          <div className="llm-card">
                            <h4>📅 Application Timing & Method</h4>
                            {llmResult.application_guide.map((step, i) => (
                              <div key={i} className="app-step">
                                <div className="app-step-header">
                                  <span className="step-num">{i + 1}</span>
                                  <strong>{step.stage}</strong>
                                </div>
                                <div className="app-step-body">
                                  <p><strong>When:</strong> {step.timing}</p>
                                  <p><strong>How:</strong> {step.method}</p>
                                  <p><strong>Precautions:</strong> {step.precautions}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Cost Analysis */}
                        {llmResult.cost_analysis && (
                          <div className="llm-card cost-card">
                            <h4>💰 Cost Analysis for {llmResult.cost_analysis.farm_size_acres} Acres</h4>
                            {llmResult.cost_analysis.items?.length > 0 && (
                              <table className="llm-table">
                                <thead>
                                  <tr>
                                    <th>Product</th>
                                    <th>Quantity Required</th>
                                    <th>Unit Price (₹)</th>
                                    <th>Total Cost (₹)</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {llmResult.cost_analysis.items.map((item, i) => (
                                    <tr key={i}>
                                      <td>{item.product_name}</td>
                                      <td>{item.quantity_required}</td>
                                      <td>{item.unit_price_inr}</td>
                                      <td className="cost-val">{item.total_cost_inr}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            )}
                            <div className="cost-summary">
                              {llmResult.cost_analysis.labour_cost_inr && (
                                <div className="cost-row">
                                  <span>Labour / Spraying Cost</span>
                                  <span>₹ {llmResult.cost_analysis.labour_cost_inr}</span>
                                </div>
                              )}
                              <div className="cost-row total">
                                <span>Total Estimated Cost</span>
                                <span>₹ {llmResult.cost_analysis.total_estimated_cost_inr}</span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {llmResult?.parse_error && (
                      <div className="llm-card">
                        <h4>AI Response</h4>
                        <pre className="llm-raw">{llmResult.raw_response}</pre>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
