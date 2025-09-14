import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

export const uploadResume = (file, onUploadProgress) => {
  const data = new FormData();
  data.append("file", file);
  return axios.post(`${API_BASE}/api/upload`, data, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress
  });
};

export const fetchResumes = () => axios.get(`${API_BASE}/api/resumes`);
export const fetchResumeDetail = (id) => axios.get(`${API_BASE}/api/resumes/${id}`);
