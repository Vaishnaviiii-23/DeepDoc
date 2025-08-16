import React, { useState } from "react";
import { FaUpload } from "react-icons/fa";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [gender, setGender] = useState("male"); // default gender

const API_URL =
  process.env.NODE_ENV === "production"
    ? process.env.REACT_APP_API_URL || "https://deepdoc-1ox2.onrender.com"
    : "http://localhost:8000";


  async function handleUpload(e) {
    e.preventDefault();
    if (!file) {
      setStatus("Please select a file first");
      return;
    }
    setStatus("");
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("gender", gender); // send gender to backend if needed

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();
      setResult(data);
      setStatus("Upload successful");
    } catch (error) {
      console.error(error);
      setStatus("Upload failed");
    } finally {
      setLoading(false);
    }
  }

  function isNormal(meaning) {
    return meaning?.toLowerCase().includes("within normal");
  }

  function renderNormalRange(range) {
    if (typeof range === "string") {
      return range;
    } else if (typeof range === "object" && range !== null) {
      return range[gender] || "N/A";
    }
    return "N/A";
  }

  function groupParameters(parameters) {
    const groups = {
      CBC: {},
      Liver: {},
      Kidney: {},
      Other: {},
    };

    Object.entries(parameters).forEach(([param, info]) => {
      const name = param.toLowerCase();
      if (
        name.includes("hemoglobin") ||
        name.includes("wbc") ||
        name.includes("platelet") ||
        name.includes("rbc") ||
        name.includes("hematocrit")
      ) {
        groups.CBC[param] = info;
      } else if (
        name.includes("bilirubin") ||
        name.includes("ast") ||
        name.includes("alt") ||
        name.includes("alkaline phosphatase") ||
        name.includes("albumin")
      ) {
        groups.Liver[param] = info;
      } else if (
        name.includes("creatinine") ||
        name.includes("urea") ||
        name.includes("bun") ||
        name.includes("egfr")
      ) {
        groups.Kidney[param] = info;
      } else {
        groups.Other[param] = info;
      }
    });

    return groups;
  }

  function renderGroup(title, groupData) {
    if (Object.keys(groupData).length === 0) return null;
    return (
      <details className="group-section" open>
        <summary className="group-title">{title}</summary>
        {Object.entries(groupData).map(([param, info]) => (
          <div key={param} className="medical-card">
            <h4>{param}</h4>
            <p><strong>Value:</strong> {info.value}</p>
            <p><strong>Normal Range:</strong> {renderNormalRange(info.normal_range)}</p>
            <details>
              <summary>Description</summary>
              <p>{info.description}</p>
            </details>
            <p>
              <strong>Meaning:</strong>{" "}
              <span
                style={{
                  color: isNormal(info.meaning) ? "green" : "red",
                  fontWeight: "bold",
                }}
              >
                {info.meaning}
              </span>
            </p>
            <details>
              <summary>Medical Advice</summary>
              <p>{info.advice}</p>
            </details>
          </div>
        ))}
      </details>
    );
  }

  return (
    <>
      <header className="header">
        <div className="container header-container">
          <h1 className="logo">🩺👩‍⚕️DeepDoc</h1>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="container hero-content">
            <h2>Real-Time Medical Report Translator & Visualizer</h2>
            <p>
              Upload your medical reports and get instant, detailed,
              easy-to-understand explanations powered by AI.
            </p>
          </div>
        </section>

        <section className="upload-section">
          <div className="container upload-container">

            {/* Gender Selector */}
            <div style={{ marginBottom: "15px" }}>
              <label><strong>Select Gender: </strong></label>
              <select value={gender} onChange={(e) => setGender(e.target.value)}>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            <form onSubmit={handleUpload} className="upload-form">
              <input
                type="file"
                accept=".pdf,image/*"
                onChange={(e) => setFile(e.target.files[0])}
                className="file-input"
              />
              <button type="submit" className="upload-button" disabled={loading}>
                <FaUpload style={{ marginRight: "8px" }} />
                {loading ? "Uploading..." : "Upload Report"}
              </button>
            </form>

            {status && <p className="status-message">{status}</p>}

            {result && (
              <div className="result-container">
                <h3>Extracted Medical Report Explanation</h3>
                <p><strong>Filename:</strong> {result.filename}</p>

                {Object.keys(result.parsed_results).length === 0 && (
                  <p>No recognized medical parameters found in the report.</p>
                )}

                {(() => {
                  const grouped = groupParameters(result.parsed_results);
                  return (
                    <>
                      {renderGroup("Complete Blood Count (CBC)", grouped.CBC)}
                      {renderGroup("Liver Function Tests", grouped.Liver)}
                      {renderGroup("Kidney Function Tests", grouped.Kidney)}
                      {renderGroup("Other Parameters", grouped.Other)}
                    </>
                  );
                })()}

                <details className="raw-text-section">
                  <summary>Show Raw Extracted Text (from OCR)</summary>
                  <pre>{result.raw_text}</pre>
                </details>
              </div>
            )}
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="container footer-container">
          <p>© 2025 DeepDoc by Vaishnavi P Poojari</p>
        </div>
      </footer>
    </>
  );
}

export default App;
