"""
models.py
---------------------------------------------------------------------------
Modelos ORM (SQLAlchemy) que mapeiam as tabelas do banco SQLite.

Tabelas:
  orders      → pedidos
  order_items → itens de cada pedido (relação 1:N com orders)
---------------------------------------------------------------------------
"""

import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base


class OrderModel(Base):
    """Tabela `orders` — armazena cabeçalho do pedido."""

    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, index=True)
    total      = Column(Float, nullable=False)
    status     = Column(String(20), nullable=False, default="pending")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relação 1:N com OrderItemModel
    # cascade="all, delete-orphan" → apagar o pedido apaga os itens também
    items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItemModel(Base):
    """Tabela `order_items` — itens individuais de cada pedido."""

    __tablename__ = "order_items"

    id         = Column(Integer, primary_key=True, index=True)
    order_id   = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    name       = Column(String(255), nullable=False)
    price      = Column(Float, nullable=False)

    order = relationship("OrderModel", back_populates="items")
