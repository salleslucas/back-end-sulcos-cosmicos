# Sulcos Cósmicos — Back-end

API REST construída com **FastAPI** para o e-commerce de vinis **Sulcos Cósmicos**.

---

## Pré-requisitos

- Python 3.10+

---

## Executando com Docker (recomendado)

```bash
# Sobe o container (build automático na primeira vez)
docker compose up --build

# Em segundo plano
docker compose up -d --build

# Parar
docker compose down
```

O servidor ficará disponível em **http://localhost:8000**.  
A documentação interativa (Swagger UI) estará em **http://localhost:8000/docs**.

---

## Executando sem Docker (ambiente local)

```bash
# 1. Crie e ative um ambiente virtual
python -m venv venv
source venv/Scripts/activate   # Windows (bash)
# source venv/bin/activate     # macOS / Linux

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie o servidor
uvicorn main:app --reload
```

O servidor ficará disponível em **http://localhost:8000**.  
A documentação interativa (Swagger UI) estará em **http://localhost:8000/docs**.

---

## Rotas

| Método   | Endpoint          | Descrição                        |
|----------|-------------------|----------------------------------|
| `GET`    | `/orders`         | Lista todos os pedidos           |
| `POST`   | `/orders`         | Cria um novo pedido              |
| `PUT`    | `/orders/{id}`    | Atualiza o status do pedido      |
| `DELETE` | `/orders/{id}`    | Remove um pedido                 |

### Status válidos
`pending` → `shipped` → `delivered`

---

## Estrutura do front-end (integração)

```
frontend/src/
├── services/
│   ├── api.js          ← cliente HTTP base (fetch + tratamento de erros)
│   └── orders.js       ← funções getOrders / createOrder / updateOrder / deleteOrder
├── hooks/
│   └── useOrders.js    ← custom hook com estado, loading, error e success
├── components/
│   └── Feedback.jsx    ← componente de feedback visual (erro/sucesso)
└── pages/
    ├── OrdersPage.jsx  ← exemplo de listagem + atualização + remoção
    └── CartPage.jsx    ← exemplo de criação de pedido a partir do carrinho
```

---

## Como integrar ao seu front-end existente

### 1. Copie os arquivos de `frontend/src/` para o seu projeto React

### 2. Use o hook `useOrders` nos seus componentes

```jsx
import { useOrders } from "../hooks/useOrders";

function MeuComponente() {
  const {
    orders,          // lista de pedidos
    loading,         // boolean
    error,           // string ou null
    success,         // string ou null
    handleCreateOrder,
    handleUpdateOrder,
    handleDeleteOrder,
  } = useOrders();
  // ...
}
```

### 3. Crie um pedido ao finalizar o carrinho

```jsx
// cartItems vem do seu estado/contexto de carrinho
const cartItems = cartItems.map((item) => ({
  productId: item.id,
  name: item.title,
  price: item.price,
}));

await handleCreateOrder(cartItems, total);
```

### 4. Mostre feedback visual

```jsx
import Feedback from "../components/Feedback";

// No JSX:
<Feedback error={error} success={success} />
```
