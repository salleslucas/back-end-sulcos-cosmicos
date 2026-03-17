// src/components/Feedback.jsx
// ---------------------------------------------------------------------------
// Componente reutilizável de feedback visual (erro / sucesso).
// Renderize-o no topo de qualquer página que use useOrders.
// ---------------------------------------------------------------------------

import React from "react";

export default function Feedback({ error, success }) {
  if (!error && !success) return null;

  const isError = Boolean(error);
  const message = error ?? success;

  const style = {
    padding: "12px 20px",
    borderRadius: "8px",
    marginBottom: "16px",
    fontWeight: 500,
    backgroundColor: isError ? "#ffe4e4" : "#e4ffe8",
    color: isError ? "#c0392b" : "#27ae60",
    border: `1px solid ${isError ? "#e74c3c" : "#2ecc71"}`,
  };

  return <div style={style}>{message}</div>;
}
