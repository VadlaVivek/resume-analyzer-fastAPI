import React, { useState } from "react";
import ResumeUploader from "./components/ResumeUploader";
import PastResumesTable from "./components/PastResumesTable";
import ResumeDetails from "./components/ResumeDetails";

function App() {
  const [activeTab, setActiveTab] = useState("analyze");
  const [latestResult, setLatestResult] = useState(null);

  return (
    <div style={{ maxWidth: 1000, margin: "40px auto", padding: 16 }}>
      <h1>Resume Analyzer</h1>
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button style={{borderRadius: 5, borderWidth: 0}} onClick={() => setActiveTab("analyze")} disabled={activeTab==="analyze"}>Resume Analysis</button>
        <button style={{borderRadius: 5, borderWidth: 0}} onClick={() => setActiveTab("history")} disabled={activeTab==="history"}>Historical Viewer</button>
      </div>

      {activeTab === "analyze" && (
        <>
          <ResumeUploader onAnalyzed={setLatestResult} />
          {latestResult && (
            <>
              <h2 style={{ marginTop: 24 }}>Analysis Result</h2>
              <ResumeDetails data={latestResult} />
            </>
          )}
        </>
      )}

      {activeTab === "history" && <PastResumesTable />}
    </div>
  );
}

export default App;
