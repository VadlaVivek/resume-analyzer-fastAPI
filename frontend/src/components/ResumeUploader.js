import React, { useState } from "react";
import { uploadResume } from "../api";

export default function ResumeUploader() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please choose a PDF file.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await uploadResume(file, (ev) => {
        if (ev.total) setProgress(Math.round((ev.loaded / ev.total) * 100));
      });
      setResult(resp.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  return (
    <div>
      <form onSubmit={onSubmit}>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} accept="application/pdf" />
        <button type="submit" disabled={loading} style={{ marginLeft: 8 }}>
          {loading ? "Analyzing..." : "Upload & Analyze"}
        </button>
        {loading && <div>Upload progress: {progress}%</div>}
      </form>
      {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
      {result && (
        <div style={{ marginTop: 16 }}>
          <h2>Analysis</h2>
          <div><strong>Filename:</strong> {result.filename}</div>
          <div><strong>Name:</strong> {result.name}</div>
          <div><strong>Email:</strong> {result.email}</div>
          <div style={{ marginTop: 12 }}>
            <h3>Extracted Data</h3>
            <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(result.extracted_data, null, 2)}</pre>
          </div>
          <div style={{ marginTop: 12 }}>
            <h3>LLM Analysis</h3>
            <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(result.llm_analysis, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
