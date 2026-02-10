# History Process API - Exemplos de Uso

## Estrutura da Tabela

```sql
CREATE TABLE history_process (
    id BIGSERIAL PRIMARY KEY,
    orders VARCHAR(64) NOT NULL,
    step VARCHAR(20) NOT NULL,
    id_situation INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_orders_step_situation UNIQUE (orders, step, id_situation)
);
```

## Regras de Validação

1. **id_situation deve ser maior que 0**
2. **Não pode existir duplicação da combinação: orders + step + id_situation**

## Endpoints Disponíveis

### 1. Criar Histórico

**POST** `/api/history-process/`

**Body:**
```json
{
  "orders": "123",
  "step": "proposta",
  "id_situation": 1
}
```

**Resposta de Sucesso (201):**
```json
{
  "message": "Histórico criado com sucesso!",
  "data": {
    "id": 1,
    "orders": "123",
    "step": "proposta",
    "id_situation": 1,
    "created_at": "2026-02-09T10:30:00Z"
  }
}
```

**Resposta de Erro - Duplicado (400):**
```json
{
  "message": "Registro já existe",
  "detail": "Já existe um registro para orders '123', step 'proposta' com id_situation 1"
}
```

**Resposta de Erro - id_situation inválido (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "id_situation"],
      "msg": "id_situation deve ser maior que 0",
      "type": "value_error"
    }
  ]
}
```

### 2. Listar Todos os Históricos (com paginação)

**GET** `/api/history-process/?skip=0&limit=100`

**Resposta (200):**
```json
{
  "total": 150,
  "items": [
    {
      "id": 3,
      "orders": "456",
      "step": "faturamento",
      "id_situation": 2,
      "created_at": "2026-02-09T12:00:00Z"
    },
    {
      "id": 2,
      "orders": "123",
      "step": "proposta",
      "id_situation": 2,
      "created_at": "2026-02-09T11:00:00Z"
    },
    {
      "id": 1,
      "orders": "123",
      "step": "proposta",
      "id_situation": 1,
      "created_at": "2026-02-09T10:30:00Z"
    }
  ]
}
```

### 3. Buscar Histórico por Pedido

**GET** `/api/history-process/orders/123`

**Resposta (200):**
```json
{
  "orders": "123",
  "total": 2,
  "items": [
    {
      "id": 2,
      "orders": "123",
      "step": "proposta",
      "id_situation": 2,
      "created_at": "2026-02-09T11:00:00Z"
    },
    {
      "id": 1,
      "orders": "123",
      "step": "proposta",
      "id_situation": 1,
      "created_at": "2026-02-09T10:30:00Z"
    }
  ]
}
```

**Resposta - Não Encontrado (404):**
```json
{
  "message": "Nenhum histórico encontrado para o pedido '999'"
}
```

### 4. Buscar Histórico por Pedido e Step

**GET** `/api/history-process/orders/123/step/proposta`

**Resposta (200):**
```json
{
  "orders": "123",
  "step": "proposta",
  "total": 2,
  "items": [
    {
      "id": 2,
      "orders": "123",
      "step": "proposta",
      "id_situation": 2,
      "created_at": "2026-02-09T11:00:00Z"
    },
    {
      "id": 1,
      "orders": "123",
      "step": "proposta",
      "id_situation": 1,
      "created_at": "2026-02-09T10:30:00Z"
    }
  ]
}
```

## Exemplos de Uso

### Cenário 1: Registro Permitido
```bash
# Primeiro registro
curl -X POST "http://localhost:8000/api/history-process/" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": "123",
    "step": "proposta",
    "id_situation": 1
  }'
# ✅ Sucesso: Registro criado

# Segundo registro (diferente id_situation)
curl -X POST "http://localhost:8000/api/history-process/" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": "123",
    "step": "proposta",
    "id_situation": 2
  }'
# ✅ Sucesso: Registro criado (id_situation diferente)
```

### Cenário 2: Registro Bloqueado (Duplicado)
```bash
# Tentativa de criar registro duplicado
curl -X POST "http://localhost:8000/api/history-process/" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": "123",
    "step": "proposta",
    "id_situation": 1
  }'
# ❌ Erro 400: Já existe um registro com essa combinação
```

### Cenário 3: Validação de id_situation
```bash
# Tentativa com id_situation = 0
curl -X POST "http://localhost:8000/api/history-process/" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": "123",
    "step": "proposta",
    "id_situation": 0
  }'
# ❌ Erro 422: id_situation deve ser maior que 0

# Tentativa com id_situation negativo
curl -X POST "http://localhost:8000/api/history-process/" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": "123",
    "step": "proposta",
    "id_situation": -1
  }'
# ❌ Erro 422: id_situation deve ser maior que 0
```

## Arquivos Criados

1. **Model**: `app/models/history_process.py`
2. **Schema**: `app/schemas/history_process.py`
3. **Service**: `app/services/history_process.py`
4. **Router**: `app/routers/history_process.py`
5. **Migration**: `alembic/versions/a1b2c3d4e5f6_add_history_process_table.py`

## Como Executar a Migration

```bash
# Aplicar a migration
alembic upgrade head

# Reverter a migration (se necessário)
alembic downgrade -1
```

## Testando a API

Após iniciar a aplicação com `python run.py` ou `uvicorn app.main:app --reload`, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
