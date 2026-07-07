# Arquitetura

## Visao geral

A aplicacao segue uma organizacao simples por camadas:

```text
Cliente HTTP
  -> FastAPI app/main.py
  -> Middleware JWT app/core/security.py
  -> Router app/routers/*
  -> Service app/services/*
  -> Model app/models/*
  -> PostgreSQL
```

## Pontos de entrada

- `app/main.py`: cria a instancia `FastAPI`, registra o middleware JWT e inclui todos os routers.
- `run.py`: sobe `app.main:app` em `0.0.0.0:8001` com reload.
- `Dockerfile`: builda a imagem e executa `uvicorn app.main:app`.

## Camadas

### Routers

Ficam em `app/routers/`.

Responsabilidades:

- Declarar URL, metodo HTTP, parametros e response model.
- Receber a sessao `AsyncSession` via `Depends(get_db)`.
- Chamar a funcao de service correspondente.

Exemplos:

- `app/routers/orders.py`: rotas de pedidos.
- `app/routers/tickets.py`: rotas de tickets.
- `app/routers/ticket/progress.py`: progresso de tickets.
- `app/routers/ticket/divergence.py`: divergencias de tickets.

### Services

Ficam em `app/services/`.

Responsabilidades:

- Executar regras de negocio.
- Consultar/alterar o banco via SQLAlchemy.
- Fazer validacoes de existencia e unicidade.
- Montar respostas de erro e sucesso.

Exemplos de regras:

- `create_product` recebe `order_id` como numero do pedido Vale (`vale_order_id`), resolve o ID interno do pedido e cria/atualiza o produto.
- `create_ticket` busca o pedido pelo `purchase_order`, associa o ticket ao pedido e atualiza `orders.ticket_id`.
- `create_price_table_entry` impede duplicidade de `pn + destination`.

### Schemas

Ficam em `app/schemas/`.

Responsabilidades:

- Validar payloads de entrada.
- Definir modelos de resposta.
- Documentar campos no OpenAPI.

### Models

Ficam em `app/models/`.

Responsabilidades:

- Declarar tabelas SQLAlchemy.
- Declarar relacionamentos.
- Definir schema PostgreSQL de cada tabela.

Todos os modelos herdam de `app/db/base.py`, que adiciona:

- `id`
- `created_at`
- `updated_at`

Excecao: `HistoryProcess` redefine `updated_at = None`.

## Banco e sessoes

`app/database.py`:

- Carrega `.env`.
- Le `DATABASE_URL` e `ECHO_SQL`.
- Cria `engine` async.
- Expoe `get_db()` para injetar `AsyncSession` nas rotas.
- Chama `Base.metadata.create_all` no startup via `init_db()`.

Mesmo com `create_all` no startup, a forma recomendada de evoluir o banco e usar Alembic:

```bash
uv run alembic upgrade head
```

## Autenticacao

`app/core/security.py` implementa:

- Hash SHA256 de senha.
- Criacao de JWT com validade de 12 horas.
- Middleware que exige `Authorization: Bearer <token>` nas rotas protegidas.

Rotas publicas:

- `/api/users/register`
- `/api/users/login`
- `/docs`
- `/openapi.json`
- `/health`

## Dominios

- Pedidos e produtos: `orders`, `products`.
- Comercial: `proposals`, `proposals_status`.
- Logistica: `shipments`, `shipments_status`.
- Suporte: `tickets`, `ticket_progresses`, `ticket_divergences`, `tickets_status`.
- Fiscal/precos: `price_table`, `tax_reference_product_supra`.
- Auditoria: `history_process`.

