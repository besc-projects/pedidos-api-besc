# API

Todas as rotas abaixo exigem JWT, exceto registro/login e docs publicas.

Header:

```http
Authorization: Bearer <token>
```

## Users

Base: `/api/users`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `POST` | `/login` | Autentica usuario e retorna `access_token`. |
| `POST` | `/register` | Cria usuario. |
| `GET` | `/me` | Retorna payload do usuario autenticado presente no request. |

Payload de registro:

```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "senha123",
  "company": "BESC"
}
```

## Orders

Base: `/api/orders`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `POST` | `/` | Cria pedido. O service define `process_id=1` e `status_code=0`. |
| `GET` | `/pending?skip=0&limit=100` | Lista pedidos pendentes (`process_id=1`, `status_code=0`). |
| `GET` | `/status?process_id=1&status_code=0&skip=0&limit=100` | Lista pedidos por processo/status. |
| `GET` | `/status/tax-reference?process_id=2&status_code=1&vale_order_id=123` | Lista pedidos com produtos e referencia fiscal. |
| `GET` | `/get_order/{id}` | Busca pedido por `vale_order_id`, apesar do nome `id`. |
| `PUT` | `/status/{id}` | Atualiza `process_id` e `status_code` pelo `vale_order_id`. |
| `PATCH` | `/{id}` | Atualiza campos do pedido pelo `vale_order_id`. |
| `DELETE` | `/{id}` | Remove pedido pelo ID interno da tabela `orders`. |

Payload de criacao:

```json
{
  "vale_order_id": 12345,
  "ticket_id": null,
  "process_id": 0,
  "status_code": 0,
  "total_value": 5000.0,
  "portal": "VALE",
  "center": "MG",
  "state": "MG",
  "cnpj": "12.345.678/0001-90",
  "date": "2026-02-01T10:00:00",
  "days_to_delivery": "30",
  "proposal_id": 1,
  "besc_order_id": 9876,
  "contract_number": "CTR-001",
  "invoice_number": "NF-001"
}
```

## Products

Base: `/api/products`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `GET` | `/{id}` | Busca produto pelo ID interno. |
| `GET` | `/order/{order_id}` | Lista produtos por `products.order_id` interno. |
| `POST` | `/bulk/order/{order_id}` | Cria/atualiza produtos em lote. Aqui `order_id` e tratado pelo service como `vale_order_id`. |
| `PUT` | `/{product_id}` | Atualiza campos do produto. |

Payload de produto:

```json
{
  "order_id": 12345,
  "item": "10",
  "part_number": "PN-001",
  "description": "Produto de exemplo",
  "ncm_code": "12345678",
  "unit": "UN",
  "unit_price": 100.5,
  "quantity": 2,
  "material": "ACO",
  "origin": "NACIONAL",
  "ipi": 5,
  "icms": 18,
  "icms_st": 0,
  "tickets_status_id": 0,
  "stock_status_id": 0
}
```

## Proposals

Base: `/api/proposals`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `POST` | `/` | Cria proposta. |
| `GET` | `/{id}` | Busca proposta por ID. |
| `GET` | `/exists/{proposal_number}` | Busca proposta pelo numero. |
| `PUT` | `/{id}` | Atualiza proposta. |
| `DELETE` | `/{id}` | Remove proposta. |

## Shipments

Base: `/api/shipments`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `POST` | `/` | Cria expedicao. |
| `GET` | `/{id}` | Busca expedicao por ID. |
| `PUT` | `/{id}` | Atualiza expedicao. |
| `DELETE` | `/{id}` | Remove expedicao. |

Payload:

```json
{
  "status_id": 1,
  "description": "Transportadora XPTO",
  "tracking_number": "BR123",
  "shipment_date": "2026-02-01"
}
```

Atencao: o schema chama o campo de entrada de `description`, mas o model `Shipment` usa a coluna `name`.

## Price Table

Base: `/api/price-table`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `POST` | `/` | Cria preco por PN e destino. |
| `GET` | `/price/{pn}?state=MG` | Busca preco por PN e UF/destino. |
| `GET` | `/` | Lista precos com `skip` e `limit`. |
| `GET` | `/{entry_id}` | Busca entrada por ID. |
| `PATCH` | `/{entry_id}` | Atualiza entrada. |
| `DELETE` | `/{entry_id}` | Remove entrada. |
| `GET` | `/check/{pn}?state=MG` | Verifica existencia de PN no destino. |

Payload:

```json
{
  "pn": "PN-001",
  "long_description": "Descricao longa",
  "description": "Descricao curta",
  "destination": "MG",
  "unit_price": 123.45
}
```

Regra: `pn + destination` deve ser unico.

## Tax Reference

Base: `/api/tax-reference`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `POST` | `/` | Cria referencia fiscal. |
| `GET` | `/product/{id_product}` | Lista referencias por produto. |
| `GET` | `/order/{vale_order_id}` | Lista referencias dos produtos de um pedido Vale. |
| `GET` | `/` | Lista referencias com paginacao. |
| `GET` | `/{entry_id}` | Busca referencia por ID. |
| `PATCH` | `/{entry_id}` | Atualiza referencia. |
| `DELETE` | `/{entry_id}` | Remove referencia. |

Payload:

```json
{
  "id_product": 10,
  "ncm_code": "12345678",
  "ipi": "5.00",
  "icms": "18.00",
  "icms_st": "0.00",
  "origin": "NACIONAL"
}
```

## Tickets

Base: `/api/tickets`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `GET` | `/?skip=0&limit=100` | Lista tickets com filtros opcionais. |
| `GET` | `/{ticket_number}` | Busca ticket pelo numero do ticket. |
| `GET` | `/{ticket_number}/divergences/items` | Lista `item_id` das divergencias do ticket. |
| `POST` | `/` | Cria ticket e associa ao pedido pelo `purchase_order`. |
| `PATCH` | `/{ticket_id}` | Atualiza ticket pelo ID interno. |
| `DELETE` | `/{ticket_id}` | Remove ticket pelo ID interno. |

Filtros da listagem:

- `status_id`
- `ticket_number`
- `purchase_order`

Payload:

```json
{
  "order_id": null,
  "ticket_number": 1001,
  "purchase_order": 12345,
  "opened_at": "2026-02-01",
  "closed_at": null,
  "observer_range_date": null,
  "status_id": 0,
  "notes": "Chamado aberto para o pedido"
}
```

## Ticket Progresses

Base: `/api/{ticket_id}/progresses`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `GET` | `/` | Lista progressos do ticket. |
| `POST` | `/` | Cria progresso. |
| `PATCH` | `/{progress_id}` | Atualiza progresso. |
| `DELETE` | `/all` | Remove todos os progressos do ticket. |

Payload:

```json
{
  "status_progress_id": 1,
  "start_date": "2026-02-01T10:00:00",
  "end_date": null
}
```

## Ticket Divergences

Base: `/api/{ticket_id}/divergences`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `GET` | `/` | Lista divergencias do ticket. |
| `POST` | `/` | Cria divergencia. |
| `PATCH` | `/{divergence_id}/{item_id}` | Atualiza divergencia. |
| `DELETE` | `/{divergence_id}/{item_id}` | Remove divergencia. |

Payload:

```json
{
  "legal_basis": "Base legal informada pelo portal",
  "purchase_order_line": 10,
  "taxes": "ICMS/IPI",
  "item_id": 55
}
```

## History Process

Base: `/api/history-process`

| Metodo | Rota | Uso |
| --- | --- | --- |
| `POST` | `/` | Registra evento de historico. |
| `GET` | `/` | Lista eventos com `skip` e `limit`. |
| `GET` | `/order/{order_id}` | Lista eventos de um pedido. |
| `GET` | `/order/{order_id}/step/{step}` | Lista eventos de um pedido em uma etapa. |

Payload:

```json
{
  "order_id": 12345,
  "step": "cadastro",
  "description": "Pedido recebido pela API",
  "severity": "info",
  "created_by": "admin@example.com",
  "occurred_at": "2026-02-01T10:00:00Z"
}
```

