// src/services/orders.js
// ---------------------------------------------------------------------------
// Camada de serviços: Pedidos
// Cada função encapsula uma operação de negócio sobre /orders.
// Os componentes React nunca chamam fetch diretamente — chamam estas funções.
// ---------------------------------------------------------------------------

import request from "./api";

// ---------------------------------------------------------------------------
// GET /orders
// Retorna a lista completa de pedidos.
// ---------------------------------------------------------------------------
export async function getOrders() {
  return request("/orders");
}

// ---------------------------------------------------------------------------
// POST /orders
// Cria um novo pedido a partir do carrinho.
//
// @param {Object} data - { items: [{productId, name, price}], total: number }
// ---------------------------------------------------------------------------
export async function createOrder(data) {
  return request("/orders", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// PUT /orders/:id
// Atualiza o status de um pedido existente.
//
// @param {number} id     - ID do pedido
// @param {string} status - "pending" | "shipped" | "delivered"
// ---------------------------------------------------------------------------
export async function updateOrder(id, status) {
  return request(`/orders/${id}`, {
    method: "PUT",
    body: JSON.stringify({ status }),
  });
}

// ---------------------------------------------------------------------------
// DELETE /orders/:id
// Remove um pedido.
//
// @param {number} id - ID do pedido a ser removido
// ---------------------------------------------------------------------------
export async function deleteOrder(id) {
  return request(`/orders/${id}`, { method: "DELETE" });
}
