# Setup, Build e Execucao

## Requisitos

- Python 3.13+ para ambiente local, conforme `pyproject.toml`.
- `uv`.
- PostgreSQL.
- Acesso a um banco com permissao para criar schemas/tabelas ou rodar migrations.

## Variaveis de ambiente

Crie `.env` na raiz:

```env
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/nome_do_banco
JWT.SECRET=troque-este-segredo
ECHO_SQL=false
```

Campos:

- `DATABASE_URL`: URL async do SQLAlchemy. Para PostgreSQL, use `postgresql+asyncpg://...`.
- `JWT.SECRET`: segredo usado para assinar os tokens JWT.
- `ECHO_SQL`: quando `true`, imprime SQL gerado pelo SQLAlchemy no console.

## Instalar dependencias

```bash
uv sync
```

## Rodar migrations

```bash
uv run alembic upgrade head
```

Para voltar uma migration:

```bash
uv run alembic downgrade -1
```

Para criar uma migration nova apos alterar modelos:

```bash
uv run alembic revision --autogenerate -m "descricao_da_mudanca"
```

Revise sempre o arquivo gerado antes de aplicar.

## Rodar localmente

Opcao padrao na porta `8000`:

```bash
uv run uvicorn app.main:app --reload
```

Opcao via `run.py` na porta `8001`:

```bash
uv run python run.py
```

URLs uteis:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Build com Docker

```bash
docker build -t api-manager-orders .
```

Rodar container:

```bash
docker run --rm -p 8000:8000 \
  -e PORT=8000 \
  -e DATABASE_URL="postgresql+asyncpg://usuario:senha@host.docker.internal:5432/nome_do_banco" \
  -e JWT.SECRET="troque-este-segredo" \
  -e ECHO_SQL=false \
  api-manager-orders
```

## Fluxo minimo de uso

1. Suba banco e API.
2. Aplique migrations.
3. Crie usuario com `POST /api/users/register`.
4. Faca login com `POST /api/users/login`.
5. Use `Authorization: Bearer <token>` nas demais rotas.

Exemplo:

```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}' | jq -r .access_token)

curl "http://localhost:8000/api/orders/pending" \
  -H "Authorization: Bearer $TOKEN"
```

