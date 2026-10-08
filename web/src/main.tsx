import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Overview } from "./app/Overview";
import "./app/overview.css";

const container = document.getElementById("root");
if (!container) throw new Error("Root element is missing");
createRoot(container).render(
  <StrictMode>
    <Overview />
  </StrictMode>,
);
