import { useEffect, useMemo, useState } from "react";

const CROP_OPTIONS = [
  { value: "cotton", label: "🌿 Cotton" },
  { value: "wheat", label: "🌾 Wheat" },
];

const COTTON_GROWTH_STAGES = [
  "Small Plant",
  "Leaf Growth",
  "Bud Formation",
  "Flowering",
  "Boll Starting",
  "Boll Maturity",
];

const WHEAT_GROWTH_STAGES = [
  "Small Plant",
  "Tillering",
  "Stem Growth",
  "Booting",
  "Ear Formation / Flowering",
  "Grain Filling",
  "Harvest Ready",
];

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

function formatConfidence(value) {
  return `${(value * 100).toFixed(2)}%`;
}

function getConfidenceLevel(confidence) {
  if (confidence >= 0.9) return { label: "High Confidence", color: "#22763a" };
  if (confidence >= 0.7)
    return { label: "Moderate Confidence", color: "#b8860b" };
  return { label: "Low Confidence", color: "#9b1f1f" };
}

function renderParagraphs(text) {
  if (!text) return null;
  const paras = text
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);
  if (paras.length <= 1) {
    return <p className="llm-para">{text.trim()}</p>;
  }
  return paras.map((p, i) => (
    <p key={i} className="llm-para">
      {p.replace(/\n/g, " ")}
    </p>
  ));
}

/* ── Helpers: safely parse a JSON-or-string value from the API ── */
function tryParseJSON(raw) {
  if (!raw) return null;
  if (typeof raw === "object") return raw;
  const text = typeof raw === "string" ? raw.trim() : "";
  if (!text.startsWith("{") && !text.startsWith("[")) return null;
  try {
    return JSON.parse(
      text
        .replace(/'/g, '"')
        .replace(/\bNone\b/g, "null")
        .replace(/\bTrue\b/g, "true")
        .replace(/\bFalse\b/g, "false"),
    );
  } catch {
    return null;
  }
}

const CAUSE_ICONS = {
  Fungus: "🍄",
  Bacteria: "🦠",
  Virus: "🧬",
  Insect: "🐛",
  Environmental: "🌦️",
};

/* ── 1. Disease Explanation ─────────────────────────────────── */
function renderDiseaseExplanation(raw) {
  const data = tryParseJSON(raw);
  if (!data) return renderParagraphs(raw);

  const icon = CAUSE_ICONS[data.cause_type] || "🔬";
  return (
    <div className="de-wrap">
      {/* Cause badge + summary */}
      <div className="de-header">
        <span className="de-cause-badge">
          {icon} {data.cause_type || "Unknown"}
        </span>
        {data.summary && <p className="de-summary">{data.summary}</p>}
      </div>

      {/* Detail paragraph */}
      {data.detail && <p className="de-detail">{data.detail}</p>}

      {/* Risk-factor chips */}
      {Array.isArray(data.risk_factors) && data.risk_factors.length > 0 && (
        <div className="de-chips-section">
          <span className="de-chips-label">⚠️ Risk factors</span>
          <div className="de-chips">
            {data.risk_factors.map((rf, i) => (
              <span key={i} className="de-chip">
                {rf}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Spreads-when callout */}
      {data.spreads_when && (
        <div className="de-spread-note">
          <span className="de-spread-icon">🔄</span>
          <span>{data.spreads_when}</span>
        </div>
      )}
    </div>
  );
}

/* ── 2. Remedy Explanation ──────────────────────────────────── */
const REMEDY_TYPE_COLORS = {
  Chemical: {
    bg: "rgba(46,125,50,0.08)",
    border: "rgba(46,125,50,0.25)",
    icon: "🧪",
  },
  Biological: {
    bg: "rgba(56,142,60,0.08)",
    border: "rgba(56,142,60,0.25)",
    icon: "🌿",
  },
  Cultural: {
    bg: "rgba(255,152,0,0.08)",
    border: "rgba(255,152,0,0.3)",
    icon: "🌾",
  },
};

function renderRemedyExplanation(raw) {
  const data = tryParseJSON(raw);
  if (!data || !Array.isArray(data.remedies)) return renderParagraphs(raw);

  return (
    <div className="rx-wrap">
      {data.remedies.map((r, i) => {
        const style = REMEDY_TYPE_COLORS[r.type] || REMEDY_TYPE_COLORS.Chemical;
        return (
          <div
            key={i}
            className="rx-card"
            style={{
              background: style.bg,
              borderColor: style.border,
            }}
          >
            <div className="rx-card-header">
              <span className="rx-icon">{style.icon}</span>
              <strong className="rx-name">{r.name}</strong>
              <span className="rx-type-badge">{r.type}</span>
            </div>
            {r.how_it_helps && <p className="rx-help">{r.how_it_helps}</p>}
            {r.after_treatment && (
              <p className="rx-after">
                <span className="rx-after-label">After treatment:</span>{" "}
                {r.after_treatment}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ── 3. Application Guide ───────────────────────────────────── */
function renderApplicationGuide(raw) {
  const data = tryParseJSON(raw);
  if (!data) return renderParagraphs(raw);

  return (
    <div className="ag-wrap">
      {/* Quick-info tiles */}
      <div className="ag-tiles">
        {data.best_time && (
          <div className="ag-tile">
            <span className="ag-tile-icon">🕐</span>
            <div>
              <span className="ag-tile-label">Best time</span>
              <span className="ag-tile-value">{data.best_time}</span>
            </div>
          </div>
        )}
        {data.method && (
          <div className="ag-tile">
            <span className="ag-tile-icon">💨</span>
            <div>
              <span className="ag-tile-label">Method</span>
              <span className="ag-tile-value">{data.method}</span>
            </div>
          </div>
        )}
        {data.repeat && (
          <div className="ag-tile">
            <span className="ag-tile-icon">🔁</span>
            <div>
              <span className="ag-tile-label">Repeat</span>
              <span className="ag-tile-value">{data.repeat}</span>
            </div>
          </div>
        )}
      </div>

      {/* Steps timeline */}
      {Array.isArray(data.steps) && data.steps.length > 0 && (
        <div className="ag-steps">
          <span className="ag-steps-title">Step-by-step</span>
          {data.steps.map((step, i) => (
            <div key={i} className="ag-step">
              <span className="ag-step-num">{i + 1}</span>
              <span className="ag-step-text">{step}</span>
            </div>
          ))}
        </div>
      )}

      {/* Precautions strip */}
      {Array.isArray(data.precautions) && data.precautions.length > 0 && (
        <div className="ag-precautions">
          <span className="ag-prec-title">⚠️ Safety precautions</span>
          <ul className="ag-prec-list">
            {data.precautions.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function renderCostAnalysis(data) {
  const text = typeof data === "string" ? data.trim() : "";

  // Try JSON parsing
  if (text.startsWith("{")) {
    try {
      const jsonStr = text
        .replace(/'/g, '"')
        .replace(/\bNone\b/g, "null")
        .replace(/\bTrue\b/g, "true")
        .replace(/\bFalse\b/g, "false");
      const parsed = JSON.parse(jsonStr);

      const options = parsed.options || parsed.items || [];
      const recommendedIdx =
        typeof parsed.recommended_index === "number"
          ? parsed.recommended_index
          : 0;
      const recommendedReason = parsed.recommended_reason || "";
      const subsidyNote =
        parsed.subsidy_scheme || parsed.subsidy_note || parsed.note || "";

      // ----- New structured options format -----
      if (
        Array.isArray(options) &&
        options.length > 0 &&
        options[0].option_label
      ) {
        return (
          <div className="cost-options-wrap">
            <p className="cost-options-hint">
              Choose <strong>any one</strong> of the following options — do NOT
              apply them together.
            </p>

            <div className="cost-options-grid">
              {options.map((opt, i) => {
                const isRec = i === recommendedIdx;
                return (
                  <div
                    key={i}
                    className={`cost-option-card${isRec ? " recommended" : ""}`}
                  >
                    {isRec && <span className="rec-badge">✅ Recommended</span>}
                    <h5 className="option-label">{opt.option_label}</h5>
                    <p className="option-product">{opt.product_name}</p>
                    {opt.why && <p className="option-why">{opt.why}</p>}
                    <div className="option-calc">
                      <span>Packs needed</span>
                      <span className="option-val">{opt.packs_needed}</span>
                    </div>
                    <div className="option-calc">
                      <span>Cost per pack</span>
                      <span className="option-val">
                        ₹{Number(opt.cost_per_pack).toLocaleString("en-IN")}
                      </span>
                    </div>
                    <div className="option-calc total">
                      <span>Total Cost</span>
                      <span className="option-val">
                        ₹{Number(opt.total_cost).toLocaleString("en-IN")}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {recommendedReason && (
              <p className="rec-reason">
                <strong>Why recommended:</strong> {recommendedReason}
              </p>
            )}

            {subsidyNote && <p className="cost-note">{subsidyNote}</p>}
          </div>
        );
      }

      // ----- Fallback: flat items array (old format) -----
      const grandTotal = parsed.grand_total;
      const medicineRows = (Array.isArray(options) ? options : [])
        .filter((item) => typeof item === "object" && item !== null)
        .map((item) => {
          const name = item.name || item.product_name || "Medicine";
          const cost =
            item.packs_needed && item.cost_per_pack && item.total_cost
              ? `${item.packs_needed} packs × ₹${Number(item.cost_per_pack).toLocaleString("en-IN")} = ₹${Number(item.total_cost).toLocaleString("en-IN")}`
              : item.total_cost
                ? `₹${Number(item.total_cost).toLocaleString("en-IN")}`
                : "";
          return { name, cost };
        });

      return (
        <div className="cost-analysis-text">
          {medicineRows.map((row, i) => (
            <div key={i} className="cost-row">
              <span>• {row.name}</span>
              <span className="cost-val">{row.cost}</span>
            </div>
          ))}
          {grandTotal !== undefined && (
            <>
              <div className="cost-divider" />
              <div className="cost-row total">
                <span>Grand Total</span>
                <span className="cost-val">
                  ₹{Number(grandTotal).toLocaleString("en-IN")}
                </span>
              </div>
            </>
          )}
          {subsidyNote && <p className="cost-note">{subsidyNote}</p>}
        </div>
      );
    } catch (_) {
      // fall through to text parsing
    }
  }

  // Plain-text fallback
  if (!text) return null;
  return (
    <div className="cost-analysis-text">
      {text.split("\n").map((line, i) => {
        const l = line.trim();
        if (!l) return null;
        return (
          <p key={i} className="llm-para">
            {l}
          </p>
        );
      })}
    </div>
  );
}

export default function App() {
  const [crop, setCrop] = useState("cotton");
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // LLM detailed recommendation state
  const [farmSize, setFarmSize] = useState("");
  const [growthStage, setGrowthStage] = useState("");
  const [severityLevel, setSeverityLevel] = useState("");
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

  const currentGrowthStages = useMemo(() => {
    return crop === "cotton" ? COTTON_GROWTH_STAGES : WHEAT_GROWTH_STAGES;
  }, [crop]);

  function handleFileSelect(selectedFile) {
    if (selectedFile && selectedFile.type.startsWith("image/")) {
      setFile(selectedFile);
      setResult(null);
      setError("");
      setLlmResult(null);
      setLlmError("");
    } else {
      setError("Please select a valid image file.");
    }
  }

  function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function handleDragEnter(e) {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }

  function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    if (e.currentTarget === e.target) {
      setIsDragging(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      handleFileSelect(droppedFiles[0]);
    }
  }

  async function fetchLlmAdvice(predictionData, acres, stage, severity) {
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
          growth_stage: stage || "Unknown",
          severity_level: severity || "Unknown",
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        // Handle 503 errors specifically
        if (response.status === 503) {
          throw new Error(
            data?.detail ||
              "The AI service is temporarily busy. Please try again in a moment.",
          );
        }
        throw new Error(
          data?.detail || "Failed to get detailed recommendation.",
        );
      }
      setLlmResult(data.detailed_recommendation);
    } catch (err) {
      const errorMsg = err.message || "Could not connect to LLM service.";
      setLlmError(errorMsg);

      // Show retry option for 503 errors
      if (errorMsg.includes("temporarily") || errorMsg.includes("try again")) {
        console.log("503 error detected - user can retry");
      }
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

    if (!severityLevel) {
      setError("Please select a disease severity level.");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("severity_level", severityLevel);
      formData.append("growth_stage", growthStage || "Unknown");
      formData.append("farm_size", String(acres));

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
        fetchLlmAdvice(data, acres, growthStage, severityLevel);
      }
    } catch (err) {
      setError(err.message || "Could not connect to API.");
    } finally {
      setLoading(false);
    }
  }

  const severity = result ? getConfidenceLevel(result.confidence) : null;
  const isHealthy = result?.predicted_class?.toLowerCase().includes("healthy");

  return (
    <div className="page">
      <div className="background-grid" aria-hidden="true" />
      <main className="app-shell">
        <section className="hero">
          <p className="eyebrow">AI Crop Diagnostic</p>
          <h1>Plant Disease Detection</h1>
          <p>
            Upload a clear leaf photo and choose the crop model. The system
            predicts the disease class and confidence in seconds.
          </p>
        </section>

        <section className="panel">
          <form className="predict-form" onSubmit={handlePredict}>
            <div className="form-section">
              <label htmlFor="crop" className="form-label">
                Select Crop Model
              </label>
              <select
                id="crop"
                value={crop}
                className="form-select"
                onChange={(e) => {
                  setCrop(e.target.value);
                  setResult(null);
                  setError("");
                  setLlmResult(null);
                  setLlmError("");
                  setGrowthStage(""); // Reset growth stage when crop changes
                }}
              >
                {CROP_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-section">
              <label htmlFor="file" className="form-label">
                Upload Leaf Image
              </label>
              <div
                className={`dropzone ${isDragging ? "dragging" : ""}`}
                onDragOver={handleDragOver}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById("file").click()}
              >
                <input
                  id="file"
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileSelect(e.target.files?.[0])}
                  style={{ display: "none" }}
                />
                <div className="dropzone-content">
                  {file ? (
                    <p className="dropzone-text">
                      {file.name} - Click or drag to change
                    </p>
                  ) : (
                    <>
                      <p className="dropzone-icon">📁</p>
                      <p className="dropzone-text">
                        Drag & drop an image here, or click to browse
                      </p>
                    </>
                  )}
                </div>
              </div>
              <p className="input-hint">
                Only cotton or wheat plant leaf images are accepted. Other
                images are rejected.
              </p>
            </div>

            <div className="form-row">
              <div className="form-section">
                <label htmlFor="farmSize" className="form-label">
                  Farm Size (acres)
                </label>
                <input
                  id="farmSize"
                  type="number"
                  min="0.1"
                  step="0.1"
                  placeholder="e.g. 5"
                  className="form-input"
                  value={farmSize}
                  onChange={(e) => setFarmSize(e.target.value)}
                />
              </div>

              <div className="form-section">
                <label htmlFor="growthStage" className="form-label">
                  Crop Growth Stage
                </label>
                <select
                  id="growthStage"
                  value={growthStage}
                  className="form-select"
                  onChange={(e) => setGrowthStage(e.target.value)}
                >
                  <option value="">Select growth stage</option>
                  {currentGrowthStages.map((stage) => (
                    <option key={stage} value={stage}>
                      {stage}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-section">
              <label htmlFor="severityLevel" className="form-label">
                Disease Severity Level
              </label>
              <select
                id="severityLevel"
                value={severityLevel}
                className="form-select"
                onChange={(e) => setSeverityLevel(e.target.value)}
              >
                <option value="">Select severity</option>
                <option value="Mild">Mild (Early symptoms)</option>
                <option value="Moderate">Moderate (Visible damage)</option>
                <option value="Severe">Severe (Extensive damage)</option>
              </select>
            </div>

            <button
              type="submit"
              className="submit-button"
              disabled={loading || llmLoading}
            >
              <span className="button-content">
                {loading
                  ? "Analyzing..."
                  : llmLoading
                    ? "Generating Report..."
                    : "Predict Disease"}
              </span>
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
                    <span
                      className={`status-badge ${isHealthy ? "healthy" : "disease"}`}
                    >
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
                      <strong style={{ color: severity.color }}>
                        {formatConfidence(result.confidence)}
                      </strong>
                    </div>
                    <div className="confidence-bar-track">
                      <div
                        className="confidence-bar-fill"
                        style={{
                          width: `${(result.confidence * 100).toFixed(1)}%`,
                          backgroundColor: severity.color,
                        }}
                      />
                    </div>
                    <span
                      className="severity-label"
                      style={{ color: severity.color }}
                    >
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
                        <p>
                          Generating detailed report for {farmSize} acres...
                        </p>
                      </div>
                    )}

                    {llmError && (
                      <div className="llm-error-container">
                        <p className="error-text">{llmError}</p>
                        <button
                          type="button"
                          className="retry-button"
                          onClick={() =>
                            fetchLlmAdvice(
                              result,
                              parseFloat(farmSize),
                              growthStage,
                              severityLevel,
                            )
                          }
                          disabled={llmLoading}
                        >
                          🔄 Retry
                        </button>
                      </div>
                    )}

                    {llmResult && (
                      <div className="llm-result">
                        {/* 1. Why Did This Disease Happen? */}
                        {llmResult.disease_explanation && (
                          <div className="llm-card">
                            <h4>🌱 Why Did This Disease Happen?</h4>
                            {renderDiseaseExplanation(
                              llmResult.disease_explanation,
                            )}
                          </div>
                        )}

                        {/* 2. Remedy Explanation */}
                        {llmResult.remedy_explanation && (
                          <div className="llm-card">
                            <h4>💊 Recommended Remedies</h4>
                            {renderRemedyExplanation(
                              llmResult.remedy_explanation,
                            )}
                          </div>
                        )}

                        {/* 3. Application Guide */}
                        {llmResult.application_guide && (
                          <div className="llm-card">
                            <h4>📋 How &amp; When to Apply</h4>
                            {renderApplicationGuide(
                              llmResult.application_guide,
                            )}
                          </div>
                        )}

                        {/* 4. Cost Analysis */}
                        {llmResult.cost_analysis && (
                          <div className="llm-card cost-card">
                            <h4>💰 Cost Analysis for {farmSize} Acres</h4>
                            {renderCostAnalysis(llmResult.cost_analysis)}
                          </div>
                        )}

                        {llmResult.model_used && (
                          <p className="llm-meta">
                            Powered by {llmResult.model_used} &nbsp;·&nbsp;{" "}
                            {llmResult.tokens_used} tokens used
                          </p>
                        )}
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
