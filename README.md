# 🏢 API Manager Orders

> **API completa de gerenciamento de pedidos, produtos, expedições, propostas e controle de preços.**

Desenvolvida com **FastAPI**, **SQLAlchemy 2.0 (async)**, **PostgreSQL**, **Python 3.13+** e autenticação **JWT**.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Autenticação](#-autenticação)
- [Endpoints da API](#-endpoints-da-api)
  - [Autenticação](#autenticação-users)
  - [Pedidos (Orders)](#pedidos-orders)
  - [Produtos (Products)](#produtos-products)
  - [Tabela de Preços (Price Table)](#tabela-de-preços-price-table)
  - [Propostas (Proposals)](#propostas-proposals)
  - [Expedições (Shipments)](#expedições-shipments)
  - [Registros Fiscais (Taxes)](#registros-fiscais-taxes)
- [Modelos de Dados](#-modelos-de-dados)
- [Exemplos de Uso](#-exemplos-de-uso)

---

## 🎯 Visão Geral

Sistema completo para gerenciamento de:
- ✅ Pedidos e status
- ✅ Produtos com tributação (ICMS/IPI)
- ✅ Tabela de preços com controle de PN (Part Number)
- ✅ Propostas comerciais
- ✅ Expedições e rastreamento
- ✅ Autenticação JWT com middleware
- ✅ Integração com portais (BESC, VALE, etc.)

## 🛠️ Tecnologias

- **FastAPI** - Framework web async de alta performance
- **SQLAlchemy 2.0** - ORM assíncrono
- **PostgreSQL** - Banco de dados relacional
- **Alembic** - Migrações de banco de dados
- **JWT** - Autenticação e autorização
- **Pydantic** - Validação de dados
- **Python 3.13+**

---

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd api-manager-orders
```

### 2. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/database
JWT.SECRET=seu_secret_key_aqui
ECHO_SQL=true
```

### 3. Instale as dependências
```bash
uv sync
```

### 4. Execute as migrações
```bash
uv run alembic upgrade head
```

### 5. Inicie o servidor
```bash
uv run uvicorn app.main:app --reload
```

A API estará disponível em: `http://localhost:8000`  
Documentação interativa: `http://localhost:8000/docs`

---

## 🔐 Autenticação

A API utiliza **JWT (JSON Web Token)** para autenticação. Todos os endpoints são protegidos, **exceto**:
- `/api/users/register`
- `/api/users/login`
- `/docs`
- `/openapi.json`

### Fluxo de Autenticação

#### 1. Registrar novo usuário
```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "senha123",
    "company": "Minha Empresa"
  }'
```

#### 2. Fazer login
```bash
curl -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "senha123"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. Usar o token em requisições
```bash
curl -X GET "http://localhost:8000/api/orders/pending" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

**⏰ Validade do Token:** 12 horas  
**🔒 Header necessário:** `Authorization: Bearer {token}`

---

## 📚 Endpoints da API

### Autenticação (Users)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/api/users/register` | Registrar novo usuário | ❌ |
| `POST` | `/api/users/login` | Fazer login | ❌ |
| `GET` | `/api/users/me` | Dados do usuário autenticado | ✅ |

---

### Pedidos (Orders)

Base URL: `/api/orders`

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/` | Criar novo pedido | ✅ |
| `GET` | `/pending` | Listar todos os pedidos | ✅ |
| `GET` | `/get_order/{id}` | Buscar pedido por ID | ✅ |
| `PUT` | `/{id}` | Atualizar status do pedido | ✅ |
| `DELETE` | `/{id}` | Deletar pedido | ✅ |

#### 📝 Schema de Pedido

**OrderCreate:**
```json
{
  "vale_order_id": 12345,
  "status_id": 1,
  "total_value": 5000.00,
  "portal": "VALE",
  "center": "SP",
  "state": "São Paulo",
  "cnpj": "12.345.678/0001-90",
  "days_to_delivery": "30",
  "proposal_id": 1,
  "besc_order_id": 9876,
  "contract_number": "CTR-2024-001",
  "invoice_number": "INV-001",
  "products": [
    {
      "item": "001",
      "part_number": "PN-12345",
      "description": "Produto A",
      "quantity": 10,
      "unit_price": 500.00
    }
  ]
}
```

---

### Produtos (Products)

Base URL: `/api/products`

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/{id}` | Buscar produto por ID | ✅ |
| `GET` | `/order/{order_id}` | Listar produtos de um pedido | ✅ |
| `POST` | `/bulk/order/{order_id}` | Criar múltiplos produtos | ✅ |

#### 📝 Schema de Produto

**ProductCreate:**
```json
{
  "item": "001",
  "tax_id": 1,
  "part_number": "PN-12345",
  "description": "Parafuso M10",
  "ncm_code": "7318.15.00",
  "unit": "PC",
  "unit_price": 2.50,
  "quantity": 100,
  "material": "Aço Inox",
  "origin": "Nacional"
}
```

---

### Tabela de Preços (Price Table)

Base URL: `/api/price-table`

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/` | Criar produto na tabela | ✅ |
| `GET` | `/` | Listar todos (paginado) | ✅ |
| `GET` | `/{entry_id}` | Buscar por ID | ✅ |
| `GET` | `/price/{pn}` | **Consultar preço por PN** | ✅ |
| `GET` | `/check/{pn}` | Verificar se PN existe | ✅ |
| `PATCH` | `/{entry_id}` | Atualizar produto | ✅ |
| `DELETE` | `/{entry_id}` | Deletar produto | ✅ |

#### 📝 Schema de Tabela de Preços

**PriceTableCreate:**
```json
{
  "pn": "PN-12345",
  "long_description": "Parafuso hexagonal M10 aço inox 304",
  "description": "Parafuso M10",
  "destination": "PRODUÇÃO",
  "unit_price": 2.50
}
```

**PriceByPNResponse (Consulta de Preço):**
```json
{
  "pn": "PN-12345",
  "unit_price": 2.50,
  "description": "Parafuso M10"
}
```

**Validações:**
- ✅ PN deve ser único (não permite duplicatas)
- ✅ Preço unitário deve ser maior que 0
- ✅ Todos os campos são obrigatórios na criação

---

### Propostas (Proposals)

Base URL: `/api/proposals`

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/` | Criar proposta | ✅ |
| `GET` | `/{id}` | Buscar proposta por ID | ✅ |
| `PUT` | `/{id}` | Atualizar proposta | ✅ |
| `DELETE` | `/{id}` | Deletar proposta | ✅ |

#### 📝 Schema de Proposta

**ProposalCreate:**
```json
{
  "proposal_number": 2024001,
  "status_id": 1
}
```

---

### Expedições (Shipments)

Base URL: `/api/shipments`

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/` | Criar expedição | ✅ |
| `GET` | `/{id}` | Buscar expedição por ID | ✅ |
| `PUT` | `/{id}` | Atualizar expedição | ✅ |
| `DELETE` | `/{id}` | Deletar expedição | ✅ |

#### 📝 Schema de Expedição

**ShipmentCreate:**
```json
{
  "status_id": 1,
  "description": "Envio via transportadora XYZ",
  "tracking_number": "BR123456789",
  "shipment_date": "2024-02-05"
}
```

---

### Registros Fiscais (Taxes)

Base URL: `/api/tax-records`

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/` | Criar registro fiscal | ✅ |
| `GET` | `/{id}` | Buscar registro por ID | ✅ |

#### 📝 Schema de Registro Fiscal

**TaxCreate:**
```json
{
  "icms": {
    "origin": "0",
    "cst": "00",
    "modal_bc": "0",
    "base_calc": 1000.00,
    "aliquot": 18.00,
    "value": 180.00
  },
  "ipi": {
    "cst": "50",
    "base_calc": 1000.00,
    "aliquot": 10.00,
    "value": 100.00
  }
}
```

**Observação:** ICMS e IPI são opcionais, mas ao menos um deve ser fornecido.

---

## 💾 Modelos de Dados

### Relacionamentos Principais

```
User (Usuários)
  ↓
Order (Pedidos)
  ├─→ 1:N Products (Produtos)
  ├─→ 1:1 Shipment (Expedição)
  ├─→ N:1 Proposal (Proposta)
  └─→ 1:N Tickets (Chamados)

Product (Produtos)
  └─→ N:1 Tax (Registro Fiscal)
      ├─→ 1:1 ICMS
      └─→ 1:1 IPI

PriceTable (Tabela de Preços)
  ↔ Independente (consulta por PN)
```

### Tabelas do Banco de Dados

| Tabela | Descrição |
|--------|-----------|
| `users` | Usuários do sistema |
| `orders` | Pedidos |
| `products` | Produtos dos pedidos |
| `price_table` | Tabela de preços (controle de PN) |
| `proposals` | Propostas comerciais |
| `shipments` | Expedições e rastreamento |
| `tax` | Registros fiscais |
| `icms` | Detalhes de ICMS |
| `ipi` | Detalhes de IPI |
| `tickets` | Chamados de suporte |
| `orders_status` | Status dos pedidos |
| `proposals_status` | Status das propostas |
| `shipment_status` | Status das expedições |
| `tickets_status` | Status dos tickets |

---

## 🧪 Exemplos de Uso

### Exemplo 1: Criando um Pedido Completo

```bash
# 1. Fazer login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "senha123"}' \
  | jq -r '.access_token')

# 2. Criar pedido com produtos
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vale_order_id": 12345,
    "status_id": 1,
    "total_value": 2500.00,
    "portal": "VALE",
    "center": "SP",
    "state": "São Paulo",
    "cnpj": "12.345.678/0001-90",
    "products": [
      {
        "item": "001",
        "part_number": "PN-001",
        "description": "Parafuso M10",
        "quantity": 100,
        "unit_price": 2.50
      },
      {
        "item": "002",
        "part_number": "PN-002",
        "description": "Porca M10",
        "quantity": 100,
        "unit_price": 1.50
      }
    ]
  }'
```

### Exemplo 2: Gerenciando Tabela de Preços

```bash
# 1. Adicionar produto na tabela de preços
curl -X POST "http://localhost:8000/api/price-table/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pn": "PN-12345",
    "long_description": "Parafuso sextavado M10 x 40mm aço inox 304",
    "description": "Parafuso M10x40",
    "destination": "PRODUÇÃO",
    "unit_price": 2.50
  }'

# 2. Consultar preço por PN
curl -X GET "http://localhost:8000/api/price-table/price/PN-12345" \
  -H "Authorization: Bearer $TOKEN"

# 3. Verificar se PN já existe (antes de criar)
curl -X GET "http://localhost:8000/api/price-table/check/PN-12345" \
  -H "Authorization: Bearer $TOKEN"

# 4. Listar todos os preços (paginação)
curl -X GET "http://localhost:8000/api/price-table/?skip=0&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

### Exemplo 3: Criando Registro Fiscal

```bash
# Criar ICMS e IPI juntos
curl -X POST "http://localhost:8000/api/tax-records/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "icms": {
      "origin": "0",
      "cst": "00",
      "modal_bc": "0",
      "base_calc": 1000.00,
      "aliquot": 18.00,
      "value": 180.00
    },
    "ipi": {
      "cst": "50",
      "base_calc": 1000.00,
      "aliquot": 10.00,
      "value": 100.00
    }
  }'
```

---

## 🔧 Migrações de Banco de Dados

```bash
# Criar nova migração
uv run alembic revision --autogenerate -m "descrição da migração"

# Aplicar migrações
uv run alembic upgrade head

# Verificar versão atual
uv run alembic current

# Reverter última migração
uv run alembic downgrade -1
```

---

## 📖 Documentação Interativa

Acesse a documentação Swagger UI em:
```
http://localhost:8000/docs
```

Recursos disponíveis:
- ✅ Testar todos os endpoints
- ✅ Ver schemas de request/response
- ✅ Autenticação integrada (botão "Authorize")
- ✅ Exemplos de código para diferentes linguagens

---

## 🛡️ Segurança

- **Autenticação JWT:** Todas as rotas protegidas por token
- **Hashing de Senhas:** SHA-256 para armazenamento seguro
- **Middleware Global:** Validação automática de tokens
- **Expiração de Token:** 12 horas de validade
- **CORS:** Configurável conforme necessidade

---

## 📝 Notas Importantes

1. **PN Único:** A tabela de preços não permite PNs duplicados
2. **Cascade Delete:** Ao deletar um pedido, todos os produtos e tickets relacionados são removidos
3. **Relacionamento 1:1:** Cada pedido tem apenas uma expedição
4. **Timestamps Automáticos:** `created_at` e `updated_at` são gerenciados automaticamente
5. **Validação Pydantic:** Todos os dados são validados antes de serem processados

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT.

---

## 👨‍💻 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Consulte a documentação em `/docs`
- Verifique os logs da aplicação

---

**Desenvolvido com ❤️ usando FastAPI e Python**
