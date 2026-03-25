"""
models.py
---------------------------------------------------------------------------
Definição dos modelos ORM (Object-Relational Mapping) via SQLAlchemy.

Este módulo mapeia as entidades do domínio da aplicação para tabelas no
banco de dados relacional SQLite. A abordagem ORM abstrai as instruções
SQL, permitindo que as operações de persistência sejam expressas em termos
de objetos Python, o que facilita a manutenção e aumenta a legibilidade do
código.

Entidades mapeadas:
  OrderModel     → tabela `orders`      (cabeçalho do pedido)
  OrderItemModel → tabela `order_items` (itens individuais de cada pedido)

A relação entre as entidades é de cardinalidade 1:N (um pedido contém
múltiplos itens), implementada por meio de chave estrangeira e da diretiva
`relationship` do SQLAlchemy.
---------------------------------------------------------------------------
"""

import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base


class OrderModel(Base):
    """
    Representa a tabela `orders` no banco de dados.

    Armazena os dados do cabeçalho de cada pedido: valor total, status atual
    e data/hora de criação. Os itens do pedido são acessíveis por meio do
    atributo `items`, carregado automaticamente pelo SQLAlchemy (lazy loading
    padrão).

    Atributos:
        id         -- Chave primária, gerada automaticamente pelo banco.
        total      -- Valor total do pedido em reais (ponto flutuante).
        status     -- Estado atual do pedido: pending, shipped ou delivered.
        created_at -- Timestamp de criação em UTC, definido automaticamente.
        items      -- Lista de OrderItemModel associados a este pedido.
    """

    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, index=True)
    total      = Column(Float, nullable=False)
    status     = Column(String(20), nullable=False, default="pending")
    created_at = Column(
        DateTime(timezone=True),
        # O timestamp é atribuído na camada da aplicação (Python) e não pelo
        # banco, garantindo o uso consistente do fuso UTC independentemente
        # da configuração do sistema operacional que hospeda o SQLite.
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relacionamento 1:N com OrderItemModel.
    # A opção cascade="all, delete-orphan" garante que, ao excluir um pedido,
    # todos os seus itens associados sejam removidos automaticamente,
    # mantendo a integridade referencial do banco.
    items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItemModel(Base):
    """
    Representa a tabela `order_items` no banco de dados.

    Cada registro corresponde a um produto incluído em um pedido. A chave
    estrangeira `order_id` vincula o item ao pedido pai, implementando a
    restrição de integridade referencial no nível do banco.

    Atributos:
        id         -- Chave primária do item.
        order_id   -- Chave estrangeira referenciando `orders.id`.
        product_id -- Identificador do produto na FakeStore API (componente externo).
        name       -- Nome do produto no momento da compra.
        price      -- Preço unitário do produto no momento da compra.
        order      -- Referência ao pedido pai (back-reference).
    """

    __tablename__ = "order_items"

    id         = Column(Integer, primary_key=True, index=True)
    order_id   = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    name       = Column(String(255), nullable=False)
    price      = Column(Float, nullable=False)

    order = relationship("OrderModel", back_populates="items")
