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
  arrowRight: (
    <>
      <path d="M5 12h14" />
      <path d="M12 5l7 7-7 7" />
    </>
  ),
};

export function Icon({ name, size = 20, className = "", color, sw }) {
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

export function formatConfidence(value) {
  return `${(value * 100).toFixed(2)}%`;
}

export function getConfidenceLevel(confidence) {
  if (confidence >= 0.9) return { label: "High Confidence", color: "#22763a" };
  if (confidence >= 0.7)
    return { label: "Moderate Confidence", color: "#b8860b" };
  return { label: "Low Confidence", color: "#9b1f1f" };
}

export function renderParagraphs(text) {
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
export function tryParseJSON(raw) {
  if (!raw) return null;
  if (typeof raw === "object") return raw;
  const text = typeof raw === "string" ? raw.trim() : "";
  if (!text.startsWith("{") && !text.startsWith("[")) return null;

  // Try parsing as-is first (already valid JSON)
  try {
    return JSON.parse(text);
  } catch {
    // fall through
  }

  // Fallback: try with Python-style replacements
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
export function renderDiseaseExplanation(raw) {
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

export function renderRemedyExplanation(raw) {
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
export function renderApplicationGuide(raw) {
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

export function renderCostAnalysis(raw) {
  const parsed = tryParseJSON(raw);

  if (parsed) {
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
  }

  // Plain-text fallback
  const text = typeof raw === "string" ? raw.trim() : "";
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
