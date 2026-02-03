# API Manager Orders

API de gerenciamento de pedidos, produtos, expedições, clientes e integrações com portais (BESC, VALE, etc.).  
Desenvolvida com **FastAPI**, **SQLAlchemy 2.0 (async)**, **Python 3.13+** e **SQLite** (configurável via `DATABASE_URL`).

---

## Funcionalidades

- Cadastro e gerenciamento de **pedidos** (`Order`)
- Associação com **clientes**, **propostas**, **pagamentos** e **status**
- Produtos com NCM, ICMS, IPI e valores unitários
- Expedição única por pedido (**1:1**)
- Tickets de suporte vinculados
- Integração com portais via `portal`, `vale_order_id`, `besc_order_id`
- Cascade automático: exclusão de produtos/tickets/expedição ao deletar pedido

---

## Estrutura de Dados (Principais Modelos)

| Modelo | Relação | Descrição |
|-------|--------|-----------|
| `Customer` | 1 → N `Order` | Cliente com múltiplos pedidos |
| `Order` | 1 → 1 `Shipment` | Um pedido tem **uma única expedição** |
| `Order` | 1 → N `Product` | Produtos do pedido |
| `Order` | 1 → N `Ticket` | Tickets de suporte |
| `Product` | N → 1 `Order` | Pertence a um pedido |
| `Shipment` | 1 → 1 `Order` | Expedição vinculada ao pedido |
| `Tax`, `ICMS`, `IPI` | 1 → N `Product` | Impostos associados |

---

## Estrutura do Projeto
```
app/
├── db/
│ ├── base.py # Base declarativa com id, created_at, updated_at
│ ├── session.py # Sessão assíncrona do SQLAlchemy
│
├── models/
│ ├── users.py # Usuários do sistema
│ ├── customers.py # Clientes
│ ├── orders.py # Pedidos
│ ├── proposals.py # Propostas
│ ├── shipments.py # Expedições
│ ├── payments.py # Pagamentos
│ ├── tickets.py # Chamados de suporte
│ ├── taxs.py # Registro tributário (Tax)
│ ├── taxes/
│ │ ├── icms.py # Imposto ICMS
│ │ └── ipi.py # Imposto IPI
│
├── schemas/
│ ├── orders.py
│ ├── taxs.py
│ ├── taxes/
│ │ ├── icms.py
│ │ └── ipi.py
│
├── services/
│ ├── orders.py
│ ├── taxes/
│ │ ├── tax.py # Serviço principal de Tax
│ │ ├── icms.py
│ │ └── ipi.py
│
├── routers/
│ ├── orders_router.py
│ ├── taxes_router.py
│
└── main.py
```


---

## Configuração do Banco

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|--------|--------|-----------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./database.db` | URL do banco (PostgreSQL, MySQL, etc.) |
| `ECHO_SQL` | `true` | Exibe SQL no console (`true`/`false`) |

---

## Inicialização

```bash
# 1. Criar ambiente
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install fastapi uvicorn sqlalchemy[asyncio] python-dotenv

# 3. Rodar
uvicorn app.main:app --reload
```


## Estrutura de Dados (Principais Modelos)

| Modelo         | Relação             | Descrição |
|----------------|---------------------|-----------|
| `Customer`     | 1 → N `Order`       | Cliente com múltiplos pedidos |
| `Order`        | 1 → 1 `Shipment`    | Um pedido tem **uma única expedição** |
| `Order`        | 1 → N `Product`     | Produtos do pedido |
| `Order`        | 1 → N `Ticket`      | Tickets de suporte |
| `Product`      | N → 1 `Order`       | Pertence a um pedido |
| `Shipment`     | 1 → 1 `Order`       | Expedição vinculada ao pedido |
| `Tax`, `ICMS`, `IPI` | 1 → N `Product` | Impostos associados |

Todos os back_populates são bidirecionais e validados com configure_mappers().


Endpoints (exemplo)
httpGET    /orders/{id}
POST   /orders/
GET    /orders/{id}/products
GET    /orders/{id}/shipment
POST   /shipments/

Estruture em app/routers/orders.py, products.py, etc.


Boas Práticas Aplicadas

configure_mappers() no startup
foreign_keys explícitos em relações ambíguas
uselist=False + single_parent=True em 1:1
cascade="all, delete-orphan" apenas no lado "one"
__init__.py importa todos os modelos
async com AsyncSession


Testes
python# tests/test_orders.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_order_with_shipment():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/orders/", json={...})
        assert response.status_code == 200

Contribuição

Fork o projeto
Crie uma branch: git checkout -b feature/nova-func
Commit: git commit -m "Adiciona X"
Push: git push origin feature/nova-func
Abra um PR


Licença
MIT © 2025.


