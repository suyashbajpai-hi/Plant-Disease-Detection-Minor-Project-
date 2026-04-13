import { useEffect, useMemo, useState } from "react";

/* ── Premium SVG Icon System ─────────────────────────────── */
const ICON_DEFS = {
  leaf: (
    <>
      <path d="M11 20A7 7 0 0 1 9.8 6C13.7 3.4 19 3 21 3c0 2-.4 7.3-3 11.2A7 7 0 0 1 11 20z" />
      <path d="M12 7l-4 4" />
    </>
  ),
  wheat: (
    <>
      <path d="M12 21V10" />
      <path d="M12 3v3" />
      <path d="M8 6c2 1.5 6 1.5 8 0" />
      <path d="M8.5 10.5c1.5 1 5.5 1 7 0" />
      <path d="M9.5 14.5c1 .75 4 .75 5 0" />
    </>
  ),
  mushroom: (
    <>
      <path d="M12 15v5" />
      <path d="M4 15a8 8 0 1 1 16 0H4z" />
    </>
  ),
  bacteria: (
    <>
      <circle cx="12" cy="12" r="4.5" />
      <path d="M12 3v4m0 10v4M3 12h4m10 0h4M5.6 5.6l2.8 2.8m7.2 7.2l2.8 2.8M5.6 18.4l2.8-2.8m7.2-7.2l2.8-2.8" />
    </>
  ),
  dna: (
    <>
      <path d="M7 4c0 3.5 5 5.5 5 8s-5 4.5-5 8" />
      <path d="M17 4c0 3.5-5 5.5-5 8s5 4.5 5 8" />
      <path d="M7 7h10M7 17h10M9 12h6" />
    </>
  ),
  bug: (
    <>
      <rect x="8" y="9" width="8" height="9" rx="4" />
      <path d="M12 9V6m-2-2l2 2 2-2M7 11l-3-1m13 1l3-1M7 15l-3 1m13-1l3 1M12 18v3" />
    </>
  ),
  cloud: <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" />,
  microscope: (
    <>
      <path d="M6 21h12" />
      <path d="M12 21v-4" />
      <circle cx="12" cy="8" r="3" />
      <path d="M12 11v6M15 6l2-2" />
    </>
  ),
  alertTriangle: (
    <>
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <path d="M12 9v4m0 4h.01" />
    </>
  ),
  refresh: (
    <>
      <path d="M21 2v6h-6" />
      <path d="M3 12a9 9 0 0 1 15-6.7L21 8" />
      <path d="M3 22v-6h6" />
      <path d="M21 12a9 9 0 0 1-15 6.7L3 16" />
    </>
  ),
  spread: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 5V2m0 20v-3M5 12H2m20 0h-3M7.05 7.05L4.93 4.93m14.14 14.14l-2.12-2.12M7.05 16.95l-2.12 2.12m14.14-14.14l-2.12 2.12" />
    </>
  ),
  flask: (
    <>
      <path d="M9 3h6" />
      <path d="M10 3v6l-6 9a1.5 1.5 0 0 0 1.3 2.2h13.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="10" />
      <path d="M12 6v6l4 2" />
    </>
  ),
  spray: (
    <path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2" />
  ),
  repeat: (
    <>
      <path d="M17 2l4 4-4 4" />
      <path d="M3 11V9a4 4 0 0 1 4-4h14" />
      <path d="M7 22l-4-4 4-4" />
      <path d="M21 13v2a4 4 0 0 1-4 4H3" />
    </>
  ),
  checkCircle: (
    <>
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <path d="M22 4L12 14.01l-3-3" />
    </>
  ),
  folder: (
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
  ),
  check: <path d="M20 6L9 17l-5-5" />,
  alertCircle: (
    <>
      <circle cx="12" cy="12" r="10" />
      <path d="M12 8v4m0 4h.01" />
    </>
  ),
  robot: (
    <>
      <rect x="3" y="8" width="18" height="12" rx="2" />
      <path d="M12 8V4" />
      <circle cx="12" cy="3" r="1" fill="currentColor" />
      <circle cx="9" cy="14" r="1.5" fill="currentColor" />
      <circle cx="15" cy="14" r="1.5" fill="currentColor" />
      <path d="M9 18h6" />
    </>
  ),
  seedling: (
    <>
      <path d="M12 22V12" />
      <path d="M12 12c0-4-5-8-9-8 0 5 5 8 9 8z" />
      <path d="M12 15c0-4 5-8 9-8 0 5-5 8-9 8z" />
    </>
  ),
  pill: (
    <>
      <rect x="5" y="2" width="14" height="20" rx="7" />
      <path d="M5 12h14" />
    </>
  ),
  clipboard: (
    <>
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
      <rect x="8" y="2" width="8" height="4" rx="1" />
    </>
  ),
  coins: (
    <>
      <ellipse cx="12" cy="7" rx="7" ry="3" />
      <path d="M19 7v4c0 1.66-3.13 3-7 3S5 12.66 5 11V7" />
      <path d="M19 11v4c0 1.66-3.13 3-7 3S5 16.66 5 15v-4" />
    </>
  ),
};

function Icon({ name, size = 20, className = "", color, sw }) {
  const content = ICON_DEFS[name];
  if (!content) return null;
  return (
    <svg
      className={`icon ${className}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={sw || 2.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={color ? { color } : undefined}
    >
      {content}
    </svg>
  );
}

const CROP_OPTIONS = [
  { value: "cotton", label: "Cotton", icon: "leaf" },
  { value: "wheat", label: "Wheat", icon: "wheat" },
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
  Fungus: "mushroom",
  Bacteria: "bacteria",
  Virus: "dna",
  Insect: "bug",
  Environmental: "cloud",
};

/* ── 1. Disease Explanation ─────────────────────────────────── */
function renderDiseaseExplanation(raw) {
  const data = tryParseJSON(raw);
  if (!data) return renderParagraphs(raw);

  const iconName = CAUSE_ICONS[data.cause_type] || "microscope";
  return (
    <div className="de-wrap">
      {/* Cause badge + summary */}
      <div className="de-header">
        <span className="de-cause-badge">
          <Icon name={iconName} size={14} /> {data.cause_type || "Unknown"}
        </span>
        {data.summary && <p className="de-summary">{data.summary}</p>}
      </div>

      {/* Detail paragraph */}
      {data.detail && <p className="de-detail">{data.detail}</p>}

      {/* Risk-factor chips */}
      {Array.isArray(data.risk_factors) && data.risk_factors.length > 0 && (
        <div className="de-chips-section">
          <span className="de-chips-label">
            <Icon name="alertTriangle" size={14} color="#e65100" /> Risk factors
          </span>
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
          <span className="de-spread-icon">
            <Icon name="spread" size={16} color="#b71c1c" />
          </span>
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
    icon: "flask",
  },
  Biological: {
    bg: "rgba(56,142,60,0.08)",
    border: "rgba(56,142,60,0.25)",
    icon: "leaf",
  },
  Cultural: {
    bg: "rgba(255,152,0,0.08)",
    border: "rgba(255,152,0,0.3)",
    icon: "wheat",
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
              <span className="rx-icon">
                <Icon name={style.icon} size={18} />
              </span>
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
            <span className="ag-tile-icon">
              <Icon name="clock" size={20} />
            </span>
            <div>
              <span className="ag-tile-label">Best time</span>
              <span className="ag-tile-value">{data.best_time}</span>
            </div>
          </div>
        )}
        {data.method && (
          <div className="ag-tile">
            <span className="ag-tile-icon">
              <Icon name="spray" size={20} />
            </span>
            <div>
              <span className="ag-tile-label">Method</span>
              <span className="ag-tile-value">{data.method}</span>
            </div>
          </div>
        )}
        {data.repeat && (
          <div className="ag-tile">
            <span className="ag-tile-icon">
              <Icon name="repeat" size={20} />
            </span>
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
          <span className="ag-prec-title">
            <Icon name="alertTriangle" size={14} color="#c62828" /> Safety
            precautions
          </span>
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
                    {isRec && (
                      <span className="rec-badge">
                        <Icon
                          name="checkCircle"
                          size={13}
                          color="#fff"
                          sw={2.5}
                        />{" "}
                        Recommended
                      </span>
                    )}
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
              <label className="form-label">Select Crop Model</label>
              <div className="crop-toggle">
                {CROP_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    className={`crop-toggle-btn${crop === option.value ? " active" : ""}`}
                    onClick={() => {
                      setCrop(option.value);
                      setResult(null);
                      setError("");
                      setLlmResult(null);
                      setLlmError("");
                      setGrowthStage("");
                    }}
                  >
                    <Icon name={option.icon} size={20} />
                    <span>{option.label}</span>
                  </button>
                ))}
              </div>
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
                      <p className="dropzone-icon">
                        <Icon
                          name="folder"
                          size={44}
                          color="#2e7d32"
                          sw={1.8}
                        />
                      </p>
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
                      {isHealthy ? (
                        <>
                          <Icon name="check" size={14} color="#fff" sw={3} />{" "}
                          Healthy
                        </>
                      ) : (
                        <>
                          <Icon
                            name="alertCircle"
                            size={14}
                            color="#fff"
                            sw={2.5}
                          />{" "}
                          Disease Detected
                        </>
                      )}
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
                    <h3>
                      <Icon name="robot" size={22} /> AI-Powered Detailed
                      Advisory
                    </h3>

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
                          <Icon name="refresh" size={15} /> Retry
                        </button>
                      </div>
                    )}

                    {llmResult && (
                      <div className="llm-result">
                        {/* 1. Why Did This Disease Happen? */}
                        {llmResult.disease_explanation && (
                          <div className="llm-card">
                            <h4>
                              <Icon name="seedling" size={18} /> Why Did This
                              Disease Happen?
                            </h4>
                            {renderDiseaseExplanation(
                              llmResult.disease_explanation,
                            )}
                          </div>
                        )}

                        {/* 2. Remedy Explanation */}
                        {llmResult.remedy_explanation && (
                          <div className="llm-card">
                            <h4>
                              <Icon name="pill" size={18} /> Recommended
                              Remedies
                            </h4>
                            {renderRemedyExplanation(
                              llmResult.remedy_explanation,
                            )}
                          </div>
                        )}

                        {/* 3. Application Guide */}
                        {llmResult.application_guide && (
                          <div className="llm-card">
                            <h4>
                              <Icon name="clipboard" size={18} /> How &amp; When
                              to Apply
                            </h4>
                            {renderApplicationGuide(
                              llmResult.application_guide,
                            )}
                          </div>
                        )}

                        {/* 4. Cost Analysis */}
                        {llmResult.cost_analysis && (
                          <div className="llm-card cost-card">
                            <h4>
                              <Icon name="coins" size={18} /> Cost Analysis for{" "}
                              {farmSize} Acres
                            </h4>
                            {renderCostAnalysis(llmResult.cost_analysis)}
                          </div>
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
