# Operacao e Troubleshooting

## Comandos frequentes

Instalar dependencias:

```bash
uv sync
```

Rodar API local:

```bash
uv run uvicorn app.main:app --reload
```

Rodar entrada alternativa:

```bash
uv run python run.py
```

Aplicar migrations:

```bash
uv run alembic upgrade head
```

Ver migration atual:

```bash
uv run alembic current
```

Ver historico:

```bash
uv run alembic history
```

## Docker

Build:

```bash
docker build -t api-manager-orders .
```

Run:

```bash
docker run --rm -p 8000:8000 \
  -e PORT=8000 \
  -e DATABASE_URL="postgresql+asyncpg://usuario:senha@host.docker.internal:5432/nome_do_banco" \
  -e JWT.SECRET="troque-este-segredo" \
  -e ECHO_SQL=false \
  api-manager-orders
```

## Autenticacao

Tokens expiram em 12 horas.

Rotas protegidas retornam `401` quando:

- Header `Authorization` nao existe.
- Header nao comeca com `Bearer `.
- Token expirou.
- Token nao foi assinado com `JWT.SECRET` atual.

## Banco

Se a API falhar no startup:

1. Confira se `DATABASE_URL` existe no `.env`.
2. Confira se a URL usa driver async: `postgresql+asyncpg://`.
3. Confira se o banco esta acessivel pela maquina/container.
4. Rode `uv run alembic upgrade head`.

## Pontos de atencao encontrados no codigo

Estes pontos nao impedem a documentacao, mas merecem cuidado em manutencoes futuras:

- `pyproject.toml` exige Python `>=3.13`, mas o `Dockerfile` usa `python:3.11-slim`.
- `app/database.py` imprime `DATABASE_URL` no startup. Isso pode vazar credenciais em logs.
- `init_db()` chama `Base.metadata.create_all` no startup. Em producao, prefira migrations Alembic controladas.
- `app/routers/orders.py` passa `process_id` e `status_code` para `get_orders_with_tax_reference_by_status`, mas a assinatura atual desse service recebe apenas `db`, `vale_order_id`, `skip` e `limit`. Essa rota tende a falhar ate a assinatura ser ajustada ou os parametros serem removidos.
- `ShipmentCreate` usa campo `description`, enquanto o model `Shipment` usa coluna `name`. Verifique esse mapeamento antes de usar a rota de expedicoes.
- Algumas rotas usam `{id}` no path mas buscam por `vale_order_id`, enquanto outras usam ID interno. Veja [`api.md`](./api.md) antes de integrar.
- `app/models/__init__.py` nao importa explicitamente `User`, `PriceTable`, `HistoryProcess` e `TaxReferenceProductSupra`, embora alguns sejam importados em `alembic/env.py`. Para autogenerate e `create_all`, mantenha imports de modelos consistentes.

## Checklist de deploy

- `DATABASE_URL` configurado.
- `JWT.SECRET` configurado com segredo forte.
- `ECHO_SQL=false`.
- Migrations aplicadas.
- Versao Python da imagem compativel com `pyproject.toml`.
- Swagger acessivel apenas onde fizer sentido operacionalmente.

