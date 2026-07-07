# History Process API

Esta API registra eventos de historico/auditoria para pedidos e etapas do processo.

## Tabela

Modelo: `app/models/history_process.py`

Tabela: `audit.history_process`

| Campo | Tipo conceitual | Uso |
| --- | --- | --- |
| `id` | bigserial | Identificador do evento. |
| `order_id` | bigint/integer | Pedido relacionado. |
| `step` | varchar(80) | Etapa do processo. |
| `description` | text | Descricao detalhada do evento. |
| `severity` | varchar(10) | `info`, `warning` ou `error`. |
| `created_by` | varchar(120) | Usuario/sistema que registrou. |
| `occurred_at` | timestamptz | Quando o evento ocorreu. |
| `created_at` | timestamptz | Quando o registro foi criado. |

## Regras

- `order_id` deve ser maior que zero.
- `step` e obrigatorio e possui limite de 80 caracteres.
- `description` e obrigatoria.
- `severity` aceita `info`, `warning` ou `error`; padrao `info`.
- Antes de criar, o service verifica duplicidade por `order_id + description`.
- Se ja existir registro igual, retorna `409`.

## Endpoints

Base: `/api/history-process`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `POST` | `/` | Cria evento de historico. |
| `GET` | `/?skip=0&limit=100` | Lista eventos, mais recentes primeiro. |
| `GET` | `/order/{order_id}` | Lista eventos de um pedido. |
| `GET` | `/order/{order_id}/step/{step}` | Lista eventos de um pedido em uma etapa. |

## Criar historico

```bash
curl -X POST "http://localhost:8000/api/history-process/" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 12345,
    "step": "cadastro",
    "description": "Pedido recebido pela API",
    "severity": "info",
    "created_by": "admin@example.com"
  }'
```

Resposta de sucesso:

```json
{
  "message": "Historico criado com sucesso!",
  "data": {
    "id": 1,
    "order_id": 12345,
    "step": "cadastro",
    "description": "Pedido recebido pela API",
    "severity": "info",
    "created_by": "admin@example.com",
    "occurred_at": "2026-02-01T10:00:00Z",
    "created_at": "2026-02-01T10:00:00Z"
  }
}
```

## Listar todos

```bash
curl "http://localhost:8000/api/history-process/?skip=0&limit=100" \
  -H "Authorization: Bearer SEU_TOKEN"
```

Resposta:

```json
{
  "total": 1,
  "items": [
    {
      "id": 1,
      "order_id": 12345,
      "step": "cadastro",
      "description": "Pedido recebido pela API",
      "severity": "info",
      "created_by": "admin@example.com",
      "occurred_at": "2026-02-01T10:00:00Z",
      "created_at": "2026-02-01T10:00:00Z"
    }
  ]
}
```

## Buscar por pedido

```bash
curl "http://localhost:8000/api/history-process/order/12345" \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Buscar por pedido e etapa

```bash
curl "http://localhost:8000/api/history-process/order/12345/step/cadastro" \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Migration

Arquivo principal:

```text
alembic/versions/a1b2c3d4e5f6_add_history_process_table.py
```

Aplicar:

```bash
uv run alembic upgrade head
```
