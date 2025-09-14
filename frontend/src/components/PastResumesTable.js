import React, { useEffect, useState } from "react";
import { fetchResumes, fetchResumeDetail } from "../api";
import ResumeDetails from "./ResumeDetails";

export default function PastResumesTable() {
  const [rows, setRows] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    try {
      const resp = await fetchResumes();
      setRows(resp.data);
    } catch (e) {
      console.error(e);
    }
  }

  async function openDetail(id) {
    setSelectedId(id);
    const resp = await fetchResumeDetail(id);
    setDetail(resp.data);
  }

  function close() {
    setSelectedId(null);
    setDetail(null);
  }

  return (
    <div>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left" }}>
            <th>id</th><th>file</th><th>Name</th><th>Email</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{r.filename}</td>
              <td>{r.name}</td>
              <td>{r.email}</td>
              <td><button onClick={() => openDetail(r.id)}>Details</button></td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedId && detail && (
        <ResumeDetails onClose={close} data={detail} />
      )}
    </div>
  );
}
