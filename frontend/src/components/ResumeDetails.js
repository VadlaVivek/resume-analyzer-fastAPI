import React from "react";

export default function ResumeDetails({ data, onClose }) {
  return (
    <div style={{
      position: "fixed", left: 0, right: 0, top: 0, bottom: 0,
      background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center"
    }}>
      <div style={{ background: "#fff", padding: 20, width: "80%", maxHeight: "80%", overflowY: "auto" }}>
        <button onClick={onClose} style={{ float: "right" }}>Close</button>
        <h2>{data.filename}</h2>
        <div><strong>Uploaded at:</strong> {data.uploaded_at}</div>
        <div><strong>Name:</strong> {data.name}</div>
        <div style={{ marginTop: 10 }}>
          <h3>Extracted Data</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(data.extracted_data, null, 2)}</pre>
        </div>
        <div style={{ marginTop: 10 }}>
          <h3>LLM Analysis</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(data.llm_analysis, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
}
