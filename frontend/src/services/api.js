// src/services/api.js
// ---------------------------------------------------------------------------
// Cliente HTTP base
// Todas as requisições para a API partem deste módulo.
// Trocar a BASE_URL aqui reflete em toda a aplicação.
// ---------------------------------------------------------------------------

const BASE_URL = "http://localhost:8000";

/**
 * Wrapper genérico de fetch com tratamento de erros centralizado.
 * Lança um Error com a mensagem recebida pelo servidor em caso de falha.
 */
async function request(endpoint, options = {}) {
  const defaultHeaders = { "Content-Type": "application/json" };

  const config = {
    ...options,
    headers: { ...defaultHeaders, ...options.headers },
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, config);

  // Respostas 204 (No Content) não possuem body
  if (response.status === 204) return null;

  const data = await response.json();

  if (!response.ok) {
    // FastAPI devolve { detail: "..." } nos erros
    const message = data?.detail ?? "Erro desconhecido na requisição.";
    throw new Error(message);
  }

  return data;
}

export default request;
