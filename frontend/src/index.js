import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.js";
import "./index.css";

// Find the root element in public/index.html
const root = ReactDOM.createRoot(document.getElementById("root"));

// Render the main App component
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
