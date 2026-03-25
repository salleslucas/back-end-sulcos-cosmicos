"""
schemas.py
---------------------------------------------------------------------------
Schemas de validação e serialização via Pydantic.

Este módulo define as estruturas de dados que trafegam pela API, separando
explicitamente a camada de contrato da API (schemas) da camada de persistência
(modelos ORM). Essa separação respeita o princípio de responsabilidade única
(SRP) e evita o acoplamento direto entre a representação interna dos dados e
a interface pública da aplicação.

Organização:
  models.py   → define COMO os dados são armazenados (SQLAlchemy / banco)
  schemas.py  → define COMO os dados trafegam nas requisições/respostas (Pydantic)

O Pydantic realiza validação automática dos tipos em tempo de execução e
gera documentação OpenAPI (Swagger) a partir das anotações de tipo definidas
neste módulo.
---------------------------------------------------------------------------
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict


# ── Enumeração de status ──────────────────────────────────────────────────────

class OrderStatus(str, Enum):
    """
    Representa os estados possíveis de um pedido ao longo do seu ciclo de vida.

    A herança de `str` permite que o Enum seja serializado diretamente como
    string no JSON de resposta, sem necessidade de conversão adicional.

    Fluxo esperado: pending → shipped → delivered
    """
    pending   = "pending"
    shipped   = "shipped"
    delivered = "delivered"


# ── Item de pedido ────────────────────────────────────────────────────────────

class OrderItemBase(BaseModel):
    """
    Schema base para um item de pedido.

    Utilizado tanto na criação (entrada) quanto como base para o schema de
    saída. Os campos refletem as informações mínimas necessárias para
    identificar e precificar um produto no contexto de um pedido.
    """
    productId: int    # ID do produto na FakeStore API (componente externo)
    name: str         # Nome do produto no momento da compra
    price: float      # Preço unitário no momento da compra


class OrderItemOut(OrderItemBase):
    """
    Schema de saída de um item de pedido.

    Estende OrderItemBase adicionando o campo `id`, que corresponde à chave
    primária do registro na tabela `order_items`. O método `from_orm_item`
    realiza o mapeamento explícito de snake_case (convenção do ORM) para
    camelCase (convenção adotada na API REST para compatibilidade com o
    front-end em JavaScript).
    """
    id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_orm_item(cls, item):
        """
        Converte um objeto OrderItemModel do ORM para o schema de saída,
        adaptando o nome do campo `product_id` → `productId`.
        """
        return cls(
            id=item.id,
            productId=item.product_id,
            name=item.name,
            price=item.price,
        )


# ── Pedido ────────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    """
    Schema de entrada para criação de um novo pedido (POST /orders).

    O campo `items` recebe a lista de produtos presentes no carrinho no
    momento do checkout. O campo `total` é calculado no front-end e enviado
    pelo cliente para evitar recálculo no servidor — em um sistema de produção,
    recomenda-se recalcular no back-end para garantir consistência.
    """
    items: List[OrderItemBase]
    total: float


class OrderUpdate(BaseModel):
    """
    Schema de entrada para atualização do status de um pedido (PUT /orders/{id}).

    Aceita apenas o campo `status`, impedindo alterações em outros atributos
    do pedido por meio deste endpoint.
    """
    status: OrderStatus


class OrderOut(BaseModel):
    """
    Schema de saída completo de um pedido.

    Retornado por todos os endpoints que produzem uma representação de pedido
    (GET /orders, POST /orders e PUT /orders/{id}). O campo `createdAt` é
    opcional para garantir compatibilidade retroativa com registros que
    eventualmente não possuam o timestamp preenchido.
    """
    id: int
    items: List[OrderItemOut]
    total: float
    status: OrderStatus
    createdAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, order):
        """
        Converte um objeto OrderModel do ORM para o schema de saída,
        delegando a conversão de cada item ao método `from_orm_item`
        de OrderItemOut.
        """
        return cls(
            id=order.id,
            items=[OrderItemOut.from_orm_item(i) for i in order.items],
            total=order.total,
            status=order.status,
            createdAt=order.created_at,
        )
