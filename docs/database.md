# Banco de Dados

O projeto usa PostgreSQL com schemas por dominio. Os modelos SQLAlchemy ficam em `app/models/` e as migrations em `alembic/versions/`.

## Base comum

A maioria das tabelas herda de `app/db/base.py`, recebendo:

| Campo | Tipo | Uso |
| --- | --- | --- |
| `id` | integer PK autoincrement | Identificador interno. |
| `created_at` | timestamptz | Criacao do registro. |
| `updated_at` | timestamptz | Atualizacao do registro. |

## Schemas

| Schema | Responsabilidade |
| --- | --- |
| `core` | Pedidos, produtos, usuarios, precos e referencias fiscais. |
| `commercial` | Propostas e status comerciais. |
| `logistics` | Expedicoes e status logisticos. |
| `support` | Tickets, progresso, divergencias e status de tickets. |
| `audit` | Historico de eventos/processos. |

## Tabelas core

### `core.orders`

Tabela central de pedidos.

| Campo | Uso |
| --- | --- |
| `id` | ID interno usado por FKs. |
| `vale_order_id` | Numero do pedido Vale. Unico e obrigatorio. Muitas rotas usam esse valor como identificador externo. |
| `besc_order_id` | Numero de pedido BESC. Unico quando informado. |
| `process_id` | Etapa macro do processo operacional. |
| `status_code` | Status dentro do processo. |
| `ticket_id` | ID do ticket mais recente associado ao pedido. |
| `state` | UF do pedido. |
| `portal` | Portal de origem. |
| `center` | Centro/localidade. |
| `contract_number` | Contrato. |
| `invoice_number` | Nota fiscal. |
| `total_value` | Valor total do pedido. |
| `cnpj` | CNPJ do cliente/empresa. |
| `days_to_delivery` | Prazo de entrega. |
| `date` | Data do pedido. |
| `version` | Versao do pedido. |
| `proposal_id` | FK para `commercial.proposals.id`. |

Relacionamentos:

- 1 pedido possui N produtos em `core.products`.
- 1 pedido possui 0 ou 1 expedicao em `logistics.shipments`.
- 1 pedido pode possuir N tickets em `support.tickets`.
- 1 pedido pode apontar para 1 proposta em `commercial.proposals`.

Uso recomendado:

- Use `id` para relacionamentos internos.
- Use `vale_order_id` para integracoes externas e buscas de pedido pela API.
- Use `process_id + status_code` para filas/telas operacionais.

### `core.products`

Produtos/itens de pedidos.

| Campo | Uso |
| --- | --- |
| `order_id` | FK para `core.orders.id`. |
| `item` | Linha/item do pedido. |
| `part_number` | PN do produto. |
| `description` | Descricao. |
| `ncm_code` | NCM. |
| `unit` | Unidade. |
| `quantity` | Quantidade. |
| `unit_price` | Preco unitario. |
| `material` | Material. |
| `origin` | Origem. |
| `payment_date` | Data de pagamento. |
| `billing_until` | Data limite de faturamento. |
| `stock_status_id` | Status de estoque. |
| `tickets_status_id` | Status relacionado a tickets. |
| `icms`, `icms_st`, `ipi` | Aliquotas fiscais no produto. |

Uso recomendado:

- Insira produtos vinculando ao pedido.
- A API de criacao em lote recebe o numero externo do pedido (`vale_order_id`) e resolve `orders.id` internamente.
- O service evita duplicidade por `part_number` ou por `item` dentro do mesmo pedido, atualizando o registro existente.

### `core.users`

Usuarios para autenticacao.

| Campo | Uso |
| --- | --- |
| `username` | Login unico. |
| `email` | Email unico. |
| `hashed_password` | Senha com hash SHA256. |
| `company` | Empresa do usuario. |

### `core.price_table`

Tabela de precos por PN e destino.

| Campo | Uso |
| --- | --- |
| `pn` | Part Number. |
| `long_description` | Descricao longa. |
| `description` | Descricao curta. |
| `destination` | Destino/UF normalizado em maiusculas. |
| `unit_price` | Preco unitario. |

Regra:

- Existe constraint unica para `pn + destination`.

Uso recomendado:

- Cadastre uma linha por PN e UF/destino.
- Consulte preco por `GET /api/price-table/price/{pn}?state=MG`.

### `core.tax_reference_product_supra`

Referencia fiscal por produto.

| Campo | Uso |
| --- | --- |
| `id_product` | ID interno de `core.products.id`. Nao ha FK declarada no model, mas e usado como relacionamento logico. |
| `ncm_code` | Codigo NCM. |
| `ipi` | Aliquota IPI. |
| `icms` | Aliquota ICMS. |
| `icms_st` | Aliquota ICMS-ST. |
| `origin` | Origem fiscal. |

Uso recomendado:

- Crie referencias apos o produto existir.
- Use `GET /api/tax-reference/order/{vale_order_id}` para obter referencias fiscais dos produtos de um pedido.

## Tabelas commercial

### `commercial.proposals`

Propostas comerciais.

| Campo | Uso |
| --- | --- |
| `proposal_number` | Numero unico da proposta. |
| `status_id` | FK para `commercial.proposals_status.id`. |
| `email` | Email relacionado a solicitacao/proposta. |
| `request_date` | Data da solicitacao. |

Relacionamento:

- `core.orders.proposal_id` aponta para `commercial.proposals.id`.

### `commercial.proposals_status`

Status de proposta.

| Campo | Uso |
| --- | --- |
| `name` | Nome do status. |
| `description` | Descricao. |

## Tabelas logistics

### `logistics.shipments`

Expedicoes.

| Campo | Uso |
| --- | --- |
| `order_id` | FK unica para `core.orders.id`. Garante uma expedicao por pedido. |
| `status_id` | FK para `logistics.shipments_status.id`. |
| `name` | Nome/descricao da expedicao ou transportadora. |
| `tracking_number` | Codigo de rastreio. |
| `shipment_date` | Data de envio. |

### `logistics.shipments_status`

Status de expedicao.

| Campo | Uso |
| --- | --- |
| `name` | Nome do status. |
| `description` | Descricao. |

## Tabelas support

### `support.tickets`

Tickets/chamados de suporte.

| Campo | Uso |
| --- | --- |
| `order_id` | FK para `core.orders.id`. |
| `ticket_number` | Numero unico do chamado. |
| `purchase_order` | Pedido de compra, usado para buscar `orders.vale_order_id` na criacao. |
| `opened_at` | Data de abertura. |
| `closed_at` | Data de fechamento. |
| `observer_range_date` | Data observada pelo fluxo quando status chega a concluido. |
| `status_id` | FK para `support.tickets_status.id`. |
| `notes` | Observacoes. |

Regra importante:

- Ao criar um ticket, o service busca o pedido por `purchase_order == orders.vale_order_id`.
- Depois de criado, `orders.ticket_id` recebe o ID do ticket mais recente.

### `support.ticket_progresses`

Etapas/progresso de um ticket.

| Campo | Uso |
| --- | --- |
| `ticket_id` | FK para `support.tickets.id`. |
| `status_progress_id` | Status da etapa de progresso. |
| `start_date` | Inicio. |
| `end_date` | Fim. |

### `support.ticket_divergences`

Divergencias vinculadas a tickets.

| Campo | Uso |
| --- | --- |
| `ticket_id` | FK para `support.tickets.id`. |
| `item_id` | ID do item/produto relacionado. |
| `legal_basis` | Base legal. |
| `purchase_order_line` | Linha da ordem de compra. |
| `taxes` | Texto com impostos/divergencias fiscais. |

Regra:

- O service evita duplicidade de divergencia por `ticket_id + item_id`.

### `support.tickets_status`

Status de tickets.

| ID | Nome esperado | Descricao |
| --- | --- | --- |
| `0` | `EM_ABERTO` | Em aberto |
| `1` | `EM_ANDAMENTO` | Em andamento |
| `2` | `CONCLUIDO` | Concluido |
| `3` | `REABERTO` | Reaberto |

A migration `c3d5e7f9a1b3_seed_ticket_status_defaults.py` cria/garante esses defaults.

## Tabelas audit

### `audit.history_process`

Historico/auditoria de eventos operacionais.

| Campo | Uso |
| --- | --- |
| `id` | BigInteger PK. |
| `order_id` | ID/numero de pedido relacionado ao evento. |
| `step` | Etapa do processo. |
| `description` | Descricao detalhada. |
| `severity` | `info`, `warning` ou `error`. |
| `created_by` | Usuario/sistema que registrou. |
| `occurred_at` | Quando o evento ocorreu. |
| `created_at` | Quando o registro foi criado. |

Regra do service:

- Antes de criar, verifica se ja existe `order_id + description`.
- Se existir, retorna HTTP `409`.

## Migrations

Comandos:

```bash
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic current
uv run alembic history
```

Observacoes:

- `alembic/env.py` carrega `DATABASE_URL` do `.env`.
- O historico de migrations tem uma revisao inicial vazia (`e780a412346d_initial_tables.py`) e migrations posteriores para precos, tickets, historico e referencias fiscais.
- Existem arquivos SQL antigos em `docs/postgres/`; trate-os como apoio/manual legado, nao como fonte principal de evolucao. A fonte principal deve ser Alembic + modelos SQLAlchemy.

