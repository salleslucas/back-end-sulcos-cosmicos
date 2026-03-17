"""
main.py
---------------------------------------------------------------------------
Sulcos Cósmicos — API REST (FastAPI + SQLite via SQLAlchemy)

Módulos do sistema:
  ┌─────────────────────────────────────────────────────────┐
  │  [EXTERNO] FakeStore API  →  catálogo de produtos       │
  │  [ESTE]    FastAPI        →  pedidos (SQLite)            │
  │  [EXTERNO] React (Vite)   →  front-end                  │
  └─────────────────────────────────────────────────────────┘

Rotas:
  GET    /orders          → listar todos os pedidos
  POST   /orders          → criar pedido (persiste no SQLite)
  PUT    /orders/{id}     → atualizar status
  DELETE /orders/{id}     → remover pedido e seus itens
  GET    /health          → health-check do container
---------------------------------------------------------------------------
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Módulos internos
from database import engine, get_db, Base
from models import OrderModel, OrderItemModel
from schemas import OrderCreate, OrderUpdate, OrderOut, OrderStatus

# Cria as tabelas no SQLite (se ainda não existirem)
Base.metadata.create_all(bind=engine)

# ── Aplicação ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sulcos Cósmicos API",
    description=(
        "API REST de pedidos para o e-commerce de vinis **Sulcos Cósmicos**.\n\n"
        "Persistência: **SQLite** via SQLAlchemy.\n\n"
        "Componente externo integrado: **FakeStore API** (catálogo de produtos)."
    ),
    version="2.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Create React App / outros bundlers
        "http://localhost:5173",   # Vite (padrão do projeto)
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health-check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Infra"], summary="Health-check do serviço")
def health():
    """Retorna `ok` — usado pelo Docker para verificar se a API está de pé."""
    return {"status": "ok", "service": "sulcos-cosmicos-api", "db": "sqlite"}


# ── GET /orders ───────────────────────────────────────────────────────────────

@app.get(
    "/orders",
    response_model=List[OrderOut],
    summary="Lista todos os pedidos",
    tags=["Pedidos"],
)
def get_orders(db: Session = Depends(get_db)):
    """Retorna todos os pedidos armazenados no SQLite, do mais recente ao mais antigo."""
    orders = db.query(OrderModel).order_by(OrderModel.id.desc()).all()
    return [OrderOut.from_orm(o) for o in orders]


# ── POST /orders ──────────────────────────────────────────────────────────────

@app.post(
    "/orders",
    response_model=OrderOut,
    status_code=201,
    summary="Cria um novo pedido",
    tags=["Pedidos"],
)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """
    Cria um novo pedido com status inicial **pending** e persiste no SQLite.

    Body esperado:
    ```json
    {
        "items": [{"productId": 3, "name": "Album Name", "price": 120}],
        "total": 120
    }
    ```
    """
    # 1. Cabeçalho do pedido
    order = OrderModel(total=data.total, status=OrderStatus.pending)
    db.add(order)
    db.flush()  # gera order.id sem fechar a transação

    # 2. Itens vinculados ao pedido
    for item in data.items:
        db.add(OrderItemModel(
            order_id=order.id,
            product_id=item.productId,
            name=item.name,
            price=item.price,
        ))

    db.commit()
    db.refresh(order)
    return OrderOut.from_orm(order)


# ── PUT /orders/{id} ──────────────────────────────────────────────────────────

@app.put(
    "/orders/{order_id}",
    response_model=OrderOut,
    summary="Atualiza o status do pedido",
    tags=["Pedidos"],
)
def update_order(order_id: int, data: OrderUpdate, db: Session = Depends(get_db)):
    """
    Atualiza o status de um pedido existente.

    Valores válidos: `pending` → `shipped` → `delivered`
    """
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Pedido {order_id} não encontrado.")

    order.status = data.status
    db.commit()
    db.refresh(order)
    return OrderOut.from_orm(order)


# ── DELETE /orders/{id} ───────────────────────────────────────────────────────

@app.delete(
    "/orders/{order_id}",
    status_code=204,
    summary="Remove um pedido",
    tags=["Pedidos"],
)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Remove permanentemente um pedido e todos os seus itens (cascade delete)."""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Pedido {order_id} não encontrado.")

    db.delete(order)
    db.commit()
