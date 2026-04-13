import { useLocation, useNavigate } from "react-router-dom";
import {
  Icon,
  formatConfidence,
  getConfidenceLevel,
  renderDiseaseExplanation,
  renderRemedyExplanation,
  renderApplicationGuide,
  renderCostAnalysis,
} from "./shared";

export default function ReportPage() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.result || !state?.llmResult) {
    return (
      <div className="page">
        <div className="background-grid" aria-hidden="true" />
        <main className="app-shell" style={{ textAlign: "center", paddingTop: "6rem" }}>
          <p>No report data available.</p>
          <button className="submit-button" style={{ marginTop: "1.5rem" }} onClick={() => navigate("/")}>
            <span className="button-content">Go Back</span>
          </button>
        </main>
      </div>
    );
  }

  const { result, llmResult, previewUrl, farmSize } = state;
  const severity = getConfidenceLevel(result.confidence);
  const isHealthy = result?.predicted_class?.toLowerCase().includes("healthy");

  return (
    <div className="page">
      <div className="background-grid" aria-hidden="true" />
      <main className="app-shell" style={{ position: "relative" }}>
        {/* Back button */}
        <button className="back-button" onClick={() => navigate("/")} style={{ position: "absolute", top: "1rem", left: "1rem", zIndex: 10 }}>
          ← Back
        </button>

        {/* Brand header */}
        <section className="hero" style={{ border: "none", boxShadow: "none", background: "transparent", paddingBottom: 0 }}>
          <div className="brand-header">
            <img src="/logo.png" alt="AgriCure" className="brand-logo" />
            <span className="brand-name">AgriCure</span>
          </div>
          <h1>Plant Disease Detection & Remedie Recommended Report</h1>
        </section>

        {/* Diagnosis card with image */}
        <section className="report-top">
          {previewUrl && (
            <div className="report-image-card">
              <img src={previewUrl} alt="Analyzed leaf" />
            </div>
          )}

          <div className="diagnosis-card">
            <div className="diagnosis-header">
              <span className={`status-badge ${isHealthy ? "healthy" : "disease"}`}>
                {isHealthy ? (
                  <>
                    <Icon name="check" size={14} color="#fff" sw={3} /> Healthy
                  </>
                ) : (
                  <>Disease Detected</>
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
              <span className="severity-label" style={{ color: severity.color }}>
                {severity.label}
              </span>
            </div>
          </div>
        </section>

        {/* Full AI Advisory */}
        {!isHealthy && llmResult && (
          <section className="result-panel">
            <div className="llm-section">
              <h3>
                <Icon name="robot" size={22} /> AI-Powered Detailed Advisory
              </h3>

              <div className="llm-result">
                {/* 1. Why Did This Disease Happen? */}
                {llmResult.disease_explanation && (
                  <div className="llm-card">
                    <h4>
                      <Icon name="seedling" size={18} /> Why Did This Disease Happen?
                    </h4>
                    {renderDiseaseExplanation(llmResult.disease_explanation)}
                  </div>
                )}

                {/* 2. Remedy Explanation */}
                {llmResult.remedy_explanation && (
                  <div className="llm-card">
                    <h4>
                      <Icon name="pill" size={18} /> Recommended Remedies
                    </h4>
                    {renderRemedyExplanation(llmResult.remedy_explanation)}
                  </div>
                )}

                {/* 3. Application Guide */}
                {llmResult.application_guide && (
                  <div className="llm-card">
                    <h4>
                      <Icon name="clipboard" size={18} /> How &amp; When to Apply
                    </h4>
                    {renderApplicationGuide(llmResult.application_guide)}
                  </div>
                )}

                {/* 4. Cost Analysis */}
                {llmResult.cost_analysis && (
                  <div className="llm-card cost-card">
                    <h4>
                      <Icon name="coins" size={18} /> Cost Analysis for {farmSize} Acres
                    </h4>
                    {renderCostAnalysis(llmResult.cost_analysis)}
                  </div>
                )}
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
