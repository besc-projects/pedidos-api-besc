# API Manager Orders

API para gerenciamento de pedidos, produtos, propostas, expedicoes, tickets, tabela de precos, referencias fiscais e historico de processos.

O projeto usa FastAPI, SQLAlchemy async, PostgreSQL, Alembic, JWT e `uv` para gerenciamento do ambiente Python.

## Documentacao

A documentacao completa fica em [`docs/README.md`](./docs/README.md).

Principais arquivos:

- [`docs/setup.md`](./docs/setup.md): como instalar, configurar, buildar e rodar.
- [`docs/architecture.md`](./docs/architecture.md): organizacao do codigo e fluxo das camadas.
- [`docs/api.md`](./docs/api.md): endpoints disponiveis e observacoes de uso.
- [`docs/database.md`](./docs/database.md): schemas, tabelas, campos, relacionamentos e migrations.
- [`docs/operations.md`](./docs/operations.md): operacao local, Docker, Alembic e troubleshooting.

## Requisitos

- Python 3.13+ para rodar localmente conforme `pyproject.toml`.
- `uv`.
- PostgreSQL acessivel pela aplicacao.

Observacao: o `Dockerfile` usa a imagem `python:3.11-slim`, enquanto o `pyproject.toml` declara `requires-python = ">=3.13"`. Veja as observacoes em [`docs/operations.md`](./docs/operations.md).

## Configuracao rapida

Crie um arquivo `.env` na raiz:

```env
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/nome_do_banco
JWT.SECRET=troque-este-segredo
ECHO_SQL=false
```

Instale dependencias:

```bash
uv sync
```

Aplique migrations:

```bash
uv run alembic upgrade head
```

Rode a API:

```bash
uv run uvicorn app.main:app --reload
```

Ou pelo arquivo de entrada local:

```bash
uv run python run.py
```

`uvicorn app.main:app --reload` sobe em `http://localhost:8000`.
`python run.py` sobe em `http://localhost:8001`.

## Autenticacao

As rotas sao protegidas por JWT, exceto:

- `POST /api/users/register`
- `POST /api/users/login`
- `/docs`
- `/openapi.json`
- `/health`

Fluxo basico:

```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"senha123","company":"BESC"}'

curl -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}'
```

Use o token retornado:

```bash
curl "http://localhost:8000/api/orders/pending" \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Estrutura resumida

```text
app/
  main.py              # instancia FastAPI, middleware JWT e routers
  database.py          # engine async, sessoes e init_db
  db/base.py           # Base SQLAlchemy com id/created_at/updated_at
  models/              # modelos/tabelas SQLAlchemy
  schemas/             # schemas Pydantic de entrada/saida
  services/            # regras de negocio e acesso ao banco
  routers/             # endpoints HTTP
alembic/               # configuracao e migrations
docs/                  # documentacao do projeto
run.py                 # entrada local na porta 8001
Dockerfile             # imagem de deploy
```

## Endpoints principais

- `/api/users`: registro, login e usuario autenticado.
- `/api/orders`: pedidos, status e consultas com produtos/referencias fiscais.
- `/api/products`: produtos vinculados a pedidos.
- `/api/proposals`: propostas comerciais.
- `/api/shipments`: expedicoes.
- `/api/price-table`: tabela de precos por PN e destino/UF.
- `/api/tax-reference`: referencias fiscais por produto/pedido.
- `/api/tickets`: tickets de suporte.
- `/api/{ticket_id}/progresses`: progresso de tickets.
- `/api/{ticket_id}/divergences`: divergencias de tickets.
- `/api/history-process`: auditoria/historico operacional.

Tambem existe Swagger em `http://localhost:8000/docs`.

## Banco de dados

O banco usa schemas PostgreSQL separados por dominio:

- `core`: pedidos, produtos, usuarios, tabela de precos e referencias fiscais.
- `commercial`: propostas e status de propostas.
- `logistics`: expedicoes e status de expedicoes.
- `support`: tickets, progresso, divergencias e status de tickets.
- `audit`: historico de processos.

Detalhes de campos e relacionamentos estao em [`docs/database.md`](./docs/database.md).

