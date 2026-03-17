// src/hooks/useOrders.js
// ---------------------------------------------------------------------------
// Custom hook: encapsula todo o estado e as operações de pedidos.
// Os componentes importam este hook e não precisam conhecer a camada de serviço.
// ---------------------------------------------------------------------------

import { useState, useEffect, useCallback } from "react";
import {
  getOrders,
  createOrder,
  updateOrder,
  deleteOrder,
} from "../services/orders";

export function useOrders() {
  const [orders, setOrders]     = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [success, setSuccess]   = useState(null);

  // -------------------------------------------------------------------------
  // Utilitário interno: limpa mensagens após 3 s
  // -------------------------------------------------------------------------
  const clearFeedback = () => {
    setTimeout(() => {
      setError(null);
      setSuccess(null);
    }, 3000);
  };

  // -------------------------------------------------------------------------
  // Buscar todos os pedidos (chamado automaticamente ao montar o componente)
  // -------------------------------------------------------------------------
  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getOrders();
      setOrders(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  // -------------------------------------------------------------------------
  // Criar pedido a partir do carrinho
  // @param {Array} cartItems  - itens do carrinho: [{productId, name, price}]
  // @param {number} total     - valor total calculado no carrinho
  // -------------------------------------------------------------------------
  const handleCreateOrder = async (cartItems, total) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const payload = { items: cartItems, total };
      const newOrder = await createOrder(payload);
      setOrders((prev) => [...prev, newOrder]);
      setSuccess("Pedido criado com sucesso! 🎵");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      clearFeedback();
    }
  };

  // -------------------------------------------------------------------------
  // Atualizar status de um pedido
  // @param {number} id     - ID do pedido
  // @param {string} status - "pending" | "shipped" | "delivered"
  // -------------------------------------------------------------------------
  const handleUpdateOrder = async (id, status) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await updateOrder(id, status);
      setOrders((prev) =>
        prev.map((order) => (order.id === id ? updated : order))
      );
      setSuccess("Status atualizado com sucesso!");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      clearFeedback();
    }
  };

  // -------------------------------------------------------------------------
  // Deletar um pedido
  // @param {number} id - ID do pedido a remover
  // -------------------------------------------------------------------------
  const handleDeleteOrder = async (id) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await deleteOrder(id);
      setOrders((prev) => prev.filter((order) => order.id !== id));
      setSuccess("Pedido removido.");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      clearFeedback();
    }
  };

  return {
    orders,
    loading,
    error,
    success,
    fetchOrders,
    handleCreateOrder,
    handleUpdateOrder,
    handleDeleteOrder,
  };
}
