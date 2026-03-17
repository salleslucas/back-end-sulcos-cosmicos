"""
schemas.py
---------------------------------------------------------------------------
Schemas Pydantic — validação de entrada e serialização de saída da API.

Separados dos modelos ORM para manter a separação de responsabilidades:
  models.py   → como os dados são ARMAZENADOS (SQLAlchemy)
  schemas.py  → como os dados TRAFEGAM pela API (Pydantic)
---------------------------------------------------------------------------
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict


# ── Enumeração de status ──────────────────────────────────────────────────────

class OrderStatus(str, Enum):
    pending   = "pending"
    shipped   = "shipped"
    delivered = "delivered"


# ── Item de pedido ────────────────────────────────────────────────────────────

class OrderItemBase(BaseModel):
    productId: int
    name: str
    price: float


class OrderItemOut(OrderItemBase):
    """Schema de saída — inclui o id do item no banco."""
    id: int

    # Mapeia snake_case do ORM → camelCase do JSON
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_orm_item(cls, item):
        return cls(
            id=item.id,
            productId=item.product_id,
            name=item.name,
            price=item.price,
        )


# ── Pedido ────────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    """Body esperado no POST /orders."""
    items: List[OrderItemBase]
    total: float


class OrderUpdate(BaseModel):
    """Body esperado no PUT /orders/{id}."""
    status: OrderStatus


class OrderOut(BaseModel):
    """Schema de saída completo do pedido."""
    id: int
    items: List[OrderItemOut]
    total: float
    status: OrderStatus
    createdAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, order):
        return cls(
            id=order.id,
            items=[OrderItemOut.from_orm_item(i) for i in order.items],
            total=order.total,
            status=order.status,
            createdAt=order.created_at,
        )
