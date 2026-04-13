import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Icon,
} from "./shared";

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

export default function App() {
  const navigate = useNavigate();
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

  // Ref to measure form height and constrain preview card
  const formRef = useRef(null);
  const panelRef = useRef(null);

  useLayoutEffect(() => {
    function syncHeight() {
      if (formRef.current && panelRef.current) {
        const h = formRef.current.offsetHeight;
        panelRef.current.style.setProperty('--form-height', `${h}px`);
      }
    }
    syncHeight();
    window.addEventListener('resize', syncHeight);
    return () => window.removeEventListener('resize', syncHeight);
  });

  // Auto-navigate to report page when LLM result is ready
  useEffect(() => {
    if (llmResult && result && previewUrl) {
      navigate("/report", {
        state: { result, llmResult, previewUrl, farmSize },
      });
    }
  }, [llmResult]);

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
      } else {
        // Healthy plant — navigate directly, no LLM needed
        navigate("/report", {
          state: { result: data, llmResult: null, previewUrl, farmSize },
        });
      }
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
          <div className="brand-header">
            <img src="/logo.png" alt="AgriCure" className="brand-logo" />
            <span className="brand-name">AgriCure</span>
          </div>
          <h1>Plant Disease Detection & Remedie Recommended</h1>
          <p className="hero-subtitle">
            Upload a clear leaf photo and choose the crop model. The system predicts the disease class and confidence in seconds.
          </p>
        </section>

        <section className="panel" ref={panelRef}>
          <form className="predict-form" ref={formRef} onSubmit={handlePredict}>
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

        {error && (
          <section className="result-panel">
            <p className="error-text">{error}</p>
          </section>
        )}

        {/* Full-page loader overlay while analyzing */}
        {(loading || llmLoading) && (
          <div className="loader-overlay">
            <div className="loader-card">
              <div className="spinner large" />
              <h3>{loading ? "Analyzing Image..." : "Generating Detailed Report..."}</h3>
              <p>{loading ? "Identifying the disease from the leaf image" : `Preparing advisory for ${farmSize} acres`}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
