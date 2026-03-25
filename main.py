"""
main.py
---------------------------------------------------------------------------
Ponto de entrada da aplicação — Sulcos Cósmicos API REST

Este módulo inicializa a aplicação FastAPI, registra os middlewares necessários
e define os endpoints da API de gerenciamento de pedidos. A arquitetura adotada
segue o padrão de separação de responsabilidades em camadas:

  ┌─────────────────────────────────────────────────────────────────────┐
  │  [Externo]  iTunes Search API  →  fornece o catálogo de álbuns     │
  │  [Este]     FastAPI / SQLite   →  gerencia pedidos (CRUD completo) │
  │  [Externo]  React / Vite       →  interface do usuário (front-end) │
  └─────────────────────────────────────────────────────────────────────┘

A persistência é realizada em banco SQLite por meio do ORM SQLAlchemy,
conforme configurado em `database.py`. Os modelos de domínio estão em
`models.py` e os schemas de validação/serialização em `schemas.py`.

Endpoints disponíveis:
  GET    /orders          → lista todos os pedidos (ordem decrescente de id)
  POST   /orders          → cria um novo pedido e persiste no banco
  PUT    /orders/{id}     → atualiza o status de um pedido existente
  DELETE /orders/{id}     → remove permanentemente um pedido e seus itens
  GET    /health          → endpoint de verificação de saúde do serviço
---------------------------------------------------------------------------
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Módulos internos do projeto
from database import engine, get_db, Base
from models import OrderModel, OrderItemModel
from schemas import OrderCreate, OrderUpdate, OrderOut, OrderStatus

# Criação das tabelas no banco de dados na inicialização da aplicação.
# O método `create_all` é idempotente: cria apenas as tabelas que ainda
# não existem, sem apagar dados previamente armazenados.
Base.metadata.create_all(bind=engine)

# ── Instância da aplicação ────────────────────────────────────────────────────
app = FastAPI(
    title="Sulcos Cósmicos API",
    description=(
        "API REST de pedidos para o e-commerce de vinis **Sulcos Cósmicos**.\n\n"
        "Persistência: **SQLite** via SQLAlchemy.\n\n"
        "Componente externo integrado: **iTunes Search API** (catálogo de álbuns)."
    ),
    version="2.0.0",
)

# ── Configuração de CORS ──────────────────────────────────────────────────────
# O middleware de CORS (Cross-Origin Resource Sharing) é necessário para
# permitir que o front-end, servido em uma origem diferente, faça requisições
# à API. Em produção, recomenda-se restringir `allow_origins` apenas ao
# domínio do front-end em vez de utilizar o caractere curinga.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Create React App / outros empacotadores
        "http://localhost:5173",   # Vite (padrão do front-end deste projeto)
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health-check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Infra"], summary="Verificação de saúde do serviço")
def health():
    """
    Retorna o estado operacional da API.

    Utilizado pelo Docker para verificar se o container está respondendo
    corretamente antes de considerá-lo saudável (healthcheck). Também pode
    ser consultado por ferramentas de monitoramento externas.
    """
    return {"status": "ok", "service": "sulcos-cosmicos-api", "db": "sqlite"}


# ── GET /orders ───────────────────────────────────────────────────────────────

@app.get(
    "/orders",
    response_model=List[OrderOut],
    summary="Lista todos os pedidos",
    tags=["Pedidos"],
)
def get_orders(db: Session = Depends(get_db)):
    """
    Recupera todos os pedidos armazenados no banco de dados.

    Os resultados são ordenados de forma decrescente pelo identificador,
    de modo que os pedidos mais recentes apareçam primeiro na listagem.
    A sessão de banco de dados é injetada automaticamente pelo FastAPI
    por meio do mecanismo de Dependency Injection.
    """
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
    Cria um novo pedido com status inicial `pending` e persiste no banco.

    A operação é realizada em uma única transação atômica: primeiro o
    cabeçalho do pedido é inserido e seu `id` é obtido via `db.flush()`
    (sem confirmar a transação), depois os itens são inseridos com a
    chave estrangeira correta. O `db.commit()` ao final confirma ambas
    as operações de forma indivisível.

    Body esperado:
    ```json
    {
        "items": [{"productId": 3, "name": "Nome do Álbum", "price": 120.0}],
        "total": 120.0
    }
    ```
    """
    # Etapa 1: insere o cabeçalho do pedido e obtém o id gerado pelo banco
    order = OrderModel(total=data.total, status=OrderStatus.pending)
    db.add(order)
    db.flush()  # envia o INSERT ao banco sem confirmar a transação, obtendo order.id

    # Etapa 2: insere cada item vinculado ao pedido recém-criado
    for item in data.items:
        db.add(OrderItemModel(
            order_id=order.id,
            product_id=item.productId,
            name=item.name,
            price=item.price,
        ))

    # Confirma ambas as operações atomicamente
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

    Caso o pedido com o `order_id` fornecido não seja encontrado, a API
    retorna HTTP 404 com uma mensagem descritiva. O status deve respeitar
    o ciclo de vida definido pela enumeração OrderStatus:
    `pending` → `shipped` → `delivered`.
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
    """
    Remove permanentemente um pedido e todos os seus itens associados.

    A exclusão em cascata é configurada no relacionamento ORM (cascade=
    "all, delete-orphan" em OrderModel.items), de modo que os registros
    da tabela `order_items` são apagados automaticamente junto com o pedido.
    Retorna HTTP 404 caso o pedido não seja encontrado, e HTTP 204 (sem
    corpo de resposta) em caso de sucesso.
    """
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Pedido {order_id} não encontrado.")

    db.delete(order)
    db.commit()
