# Sulcos Cósmicos — Back-end

API REST desenvolvida com **FastAPI** para o e-commerce de vinis Sulcos Cósmicos, como parte do trabalho acadêmico da Pós-Graduação em Desenvolvimento Full Stack da **PUC-Rio**.

---

## Descrição do Projeto

Este componente é o back-end do sistema Sulcos Cósmicos. Ele gerencia o ciclo de vida dos pedidos da loja, expondo uma API REST com operações de criação, listagem, atualização e remoção. A persistência é feita em banco de dados SQLite por meio do ORM SQLAlchemy.

O catálogo de produtos fica por conta de um serviço externo, a **iTunes Search API** (Apple), consumido diretamente pelo front-end. Ela retorna dados reais de álbuns musicais, incluindo capas, artistas e gêneros, o que a torna adequada para o contexto de uma loja de vinis. O back-end cuida apenas da lógica de pedidos, sem nenhum acoplamento com o catálogo.

### Tecnologias utilizadas

| Tecnologia      | Finalidade                                               |
|-----------------|----------------------------------------------------------|
| **FastAPI**     | Framework web assíncrono para construção da API REST     |
| **SQLAlchemy**  | ORM para mapeamento objeto-relacional e acesso ao banco  |
| **SQLite**      | Banco de dados relacional embutido (arquivo local)       |
| **Pydantic**    | Validação de dados de entrada e serialização de saída    |
| **Uvicorn**     | Servidor ASGI para execução da aplicação FastAPI         |
| **Docker**      | Conteinerização da aplicação para execução reproduzível  |

---

## Arquitetura

O projeto é organizado em camadas com responsabilidades bem definidas:

```
back-end-sulcos-cosmicos/
├── main.py            Rotas e lógica dos endpoints (controladores)
├── models.py          Modelos ORM para mapeamento das tabelas do banco
├── schemas.py         Schemas Pydantic para validação de entrada e saída
├── database.py        Configuração da conexão com o SQLite
├── requirements.txt   Dependências Python do projeto
├── Dockerfile         Imagem Docker da aplicação
└── docker-compose.yml Orquestração dos serviços em container
```

A separação entre `models.py` e `schemas.py` reflete a distinção entre a camada de persistência e a camada de apresentação da API. Os modelos definem como os dados são armazenados; os schemas definem como eles trafegam nas requisições e respostas. Isso evita que alterações internas no banco impactem diretamente o contrato público da API.

---

## Endpoints

| Método     | Endpoint           | Descrição                                      | Código de sucesso |
|------------|--------------------|------------------------------------------------|:-----------------:|
| `GET`      | `/orders`          | Lista todos os pedidos, do mais recente ao mais antigo | 200       |
| `POST`     | `/orders`          | Cria um novo pedido                            | 201               |
| `PUT`      | `/orders/{id}`     | Atualiza o status de um pedido                 | 200               |
| `DELETE`   | `/orders/{id}`     | Remove um pedido e seus itens                  | 204               |
| `GET`      | `/health`          | Verificação de saúde do serviço                | 200               |

### Ciclo de vida do status de um pedido

```
pending  ->  shipped  ->  delivered
```

### Exemplo de corpo para POST /orders

```json
{
  "items": [
    { "productId": 3, "name": "Nome do Álbum", "price": 120.0 }
  ],
  "total": 120.0
}
```

---

## Pré-requisitos

- **Docker** e **Docker Compose** (recomendado), ou
- **Python 3.10+** para execução local sem container

---

## Execução com Docker (recomendado)

```bash
# Constrói a imagem e sobe o container
docker compose up --build

# Em segundo plano
docker compose up -d --build

# Encerrar o container
docker compose down
```

A API estará disponível em **http://localhost:8000**.
A documentação interativa gerada pelo FastAPI (Swagger UI) estará em **http://localhost:8000/docs**.

---

## Execução local sem Docker

```bash
# 1. Criar e ativar o ambiente virtual Python
python -m venv venv
source venv/Scripts/activate   # Windows (bash)
# source venv/bin/activate     # macOS / Linux

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Iniciar o servidor
uvicorn main:app --reload
```

A API estará disponível em **http://localhost:8000**.

---

## Modelo de dados

### Tabela `orders`

| Campo        | Tipo       | Descrição                                 |
|--------------|------------|-------------------------------------------|
| `id`         | INTEGER PK | Identificador único do pedido             |
| `total`      | FLOAT      | Valor total do pedido                     |
| `status`     | VARCHAR    | Estado atual: pending, shipped, delivered |
| `created_at` | DATETIME   | Data e hora de criação (UTC)              |

### Tabela `order_items`

| Campo        | Tipo       | Descrição                                       |
|--------------|------------|-------------------------------------------------|
| `id`         | INTEGER PK | Identificador único do item                     |
| `order_id`   | INTEGER FK | Referência ao pedido pai (`orders.id`)          |
| `product_id` | INTEGER    | ID do álbum na iTunes Search API                |
| `name`       | VARCHAR    | Nome do produto no momento da compra            |
| `price`      | FLOAT      | Preço unitário no momento da compra             |

---

## Integração com o Front-end

O diretório `frontend/src/` contém arquivos auxiliares para facilitar a integração com esta API em projetos React:

```
frontend/src/
├── services/
│   ├── api.js       - cliente HTTP base com tratamento de erros
│   └── orders.js    - funções getOrders, createOrder, updateOrder, deleteOrder
├── hooks/
│   └── useOrders.js - custom hook com estado, loading, error e success
└── components/
    └── Feedback.jsx - componente de feedback visual para erros e confirmações
```

### Exemplo de uso do hook `useOrders`

```jsx
import { useOrders } from "../hooks/useOrders";

function MeuComponente() {
  const {
    orders,              // lista de pedidos retornada pela API
    loading,             // boolean que indica requisição em andamento
    error,               // string ou null com a mensagem de erro
    success,             // string ou null com mensagem de confirmação
    handleCreateOrder,   // (items, total) => Promise
    handleUpdateOrder,   // (id, status) => Promise
    handleDeleteOrder,   // (id) => Promise
  } = useOrders();
}
```
