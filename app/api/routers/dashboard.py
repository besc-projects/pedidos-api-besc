"""Endpoints analíticos que alimentam o dashboard React (besc-dashboard-web).

Diferente dos demais routers (CRUD sobre entidades), aqui o retorno é sempre
agregado: o navegador nunca recebe as linhas cruas para somar do lado dele.
Cada endpoint é uma consulta T-SQL enxuta contra o SQL Server.

Status canônico do pedido (apenas 4, mapeados do workflow):
  - Concretizado             -> process_id = 1 AND status_code = 4 (faturado)
  - Cancelada                -> status_code = 5
  - Confirmado               -> process_id = 1 AND status_code = 3
  - Aguardando Processamento -> todo o resto
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


# ─────────────────────────────────────────────────────────────────────────────
# Fragmentos SQL compartilhados (alias da tabela de pedidos: ``o``)
# ─────────────────────────────────────────────────────────────────────────────
FATURADO = "o.process_id = 1 AND o.status_code = 4"
CANCELADO = "o.status_code = 5"
CONFIRMADO = "o.process_id = 1 AND o.status_code = 3"
EM_ANDAMENTO = f"NOT ({FATURADO}) AND NOT ({CANCELADO})"

STATUS_CASE = """
        CASE
          WHEN o.process_id = 1 AND o.status_code = 4 THEN 'Concretizado'
          WHEN o.status_code = 5 THEN 'Cancelada'
          WHEN o.process_id = 1 AND o.status_code = 3 THEN 'Confirmado'
          ELSE 'Aguardando Processamento'
        END"""

# Condição por status canônico (filtro da página de Pedidos)
STATUS_WHERE = {
    "Concretizado": FATURADO,
    "Cancelada": CANCELADO,
    "Confirmado": CONFIRMADO,
    "Aguardando Processamento": (
        f"NOT ({FATURADO}) AND NOT ({CONFIRMADO}) "
        "AND (o.status_code IS NULL OR o.status_code <> 5)"
    ),
}

# Granularidade -> expressão que trunca a data (T-SQL, sem depender de DATETRUNC)
TRUNC = {
    "dia": "CAST(o.date AS date)",
    "semana": "CAST(DATEADD(week, DATEDIFF(week, 0, o.date), 0) AS date)",
    "mes": "CAST(DATEADD(month, DATEDIFF(month, 0, o.date), 0) AS date)",
}


# ─────────────────────────────────────────────────────────────────────────────
# Execução / serialização
# ─────────────────────────────────────────────────────────────────────────────
def _jsonable(value: Any) -> Any:
    """Decimal e datas não sobrevivem ao JSON puro — normaliza para float/ISO."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


async def _rows(db: AsyncSession, sql: str, params: dict | None = None) -> list[dict]:
    result = await db.execute(text(sql), params or {})
    return [
        {k: _jsonable(v) for k, v in row._mapping.items()}
        for row in result.fetchall()
    ]


async def _row(db: AsyncSession, sql: str, params: dict | None = None) -> dict:
    rows = await _rows(db, sql, params)
    return rows[0] if rows else {}


# ─────────────────────────────────────────────────────────────────────────────
# Filtros globais da Visão Executiva
# ─────────────────────────────────────────────────────────────────────────────
class OrderFilters:
    """Período + UF + centro, traduzidos para WHERE parametrizado."""

    def __init__(
        self,
        d1: Optional[date] = Query(None, description="Data inicial (inclusive)"),
        d2: Optional[date] = Query(None, description="Data final (inclusive)"),
        uf: Optional[str] = Query(None, description="Filial (UF)"),
        centro: Optional[str] = Query(None, description="Centro"),
    ) -> None:
        clauses = ["1=1"]
        params: dict[str, Any] = {}
        if d1 and d2:
            # ``date`` é datetime no banco: o fim do dia entra no intervalo.
            clauses.append("o.date >= :d1 AND o.date < DATEADD(day, 1, :d2)")
            params["d1"], params["d2"] = d1, d2
        if uf:
            clauses.append("o.state = :uf")
            params["uf"] = uf
        if centro:
            clauses.append("o.center = :centro")
            params["centro"] = centro
        self.where = " AND ".join(clauses)
        self.params = params


# ─────────────────────────────────────────────────────────────────────────────
# Filtros / metadados
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/filters", summary="Opções dos filtros globais (período, UF, centro)")
async def get_filters(db: AsyncSession = Depends(get_db)) -> dict:
    bounds = await _row(
        db, "SELECT min(date) AS date_min, max(date) AS date_max FROM core.orders"
    )
    states = await _rows(
        db,
        "SELECT DISTINCT state FROM core.orders WHERE state IS NOT NULL ORDER BY state",
    )
    centers = await _rows(
        db,
        "SELECT DISTINCT center FROM core.orders WHERE center IS NOT NULL ORDER BY center",
    )
    return {
        "date_min": bounds.get("date_min"),
        "date_max": bounds.get("date_max"),
        "states": [r["state"] for r in states],
        "centers": [r["center"] for r in centers],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Visão Executiva
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/overview", summary="KPIs da visão executiva")
async def get_overview(
    f: OrderFilters = Depends(), db: AsyncSession = Depends(get_db)
) -> dict:
    kpis = await _row(db, f"""
        SELECT
          count(*) AS pedidos,
          count(CASE WHEN CAST(o.date AS date) = CAST(GETDATE() AS date)
                     THEN 1 END) AS hoje,
          count(CASE WHEN o.date >= DATEADD(week, DATEDIFF(week, 0, GETDATE()), 0)
                     THEN 1 END) AS semana,
          count(CASE WHEN o.date >= DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)
                     THEN 1 END) AS mes,
          coalesce(sum(o.total_value), 0) AS valor,
          coalesce(avg(o.total_value), 0) AS ticket,
          count(CASE WHEN {EM_ANDAMENTO} THEN 1 END) AS andamento,
          count(CASE WHEN {FATURADO} THEN 1 END) AS concretizados,
          count(CASE WHEN {CONFIRMADO} THEN 1 END) AS confirmados,
          count(CASE WHEN {CANCELADO} THEN 1 END) AS cancelados,
          count(CASE WHEN ({EM_ANDAMENTO})
                      AND o.updated_at < DATEADD(hour, -48, SYSDATETIMEOFFSET())
                     THEN 1 END) AS parados,
          avg(CASE WHEN {FATURADO}
                   THEN DATEDIFF(second, o.created_at, o.updated_at) / 86400.0
              END) AS ciclo_dias
        FROM core.orders o WHERE {f.where}
    """, f.params)

    comp = await _row(db, f"""
        SELECT
          coalesce(sum(CASE WHEN o.date >= DATEADD(day, -30, CAST(GETDATE() AS date))
                            THEN o.total_value END), 0) AS atual,
          coalesce(sum(CASE WHEN o.date >= DATEADD(day, -60, CAST(GETDATE() AS date))
                             AND o.date <  DATEADD(day, -30, CAST(GETDATE() AS date))
                            THEN o.total_value END), 0) AS anterior
        FROM core.orders o WHERE {f.where}
    """, f.params)

    # "Aguardando Processamento" é o que está em andamento e ainda não foi confirmado.
    kpis["aguardando"] = int(kpis.get("andamento") or 0) - int(kpis.get("confirmados") or 0)
    return {"kpis": kpis, "comparativo": comp}


@router.get("/timeseries", summary="Evolução de pedidos por dia/semana/mês")
async def get_timeseries(
    grao: str = Query("mes", pattern="^(dia|semana|mes)$"),
    f: OrderFilters = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    trunc = TRUNC[grao]
    return await _rows(db, f"""
        SELECT {trunc} AS periodo, count(*) AS pedidos,
               coalesce(sum(o.total_value), 0) AS valor
        FROM core.orders o WHERE {f.where}
        GROUP BY {trunc} ORDER BY 1
    """, f.params)


@router.get("/billing-monthly", summary="Faturamento mensal (pedidos concretizados)")
async def get_billing_monthly(
    f: OrderFilters = Depends(), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    trunc = TRUNC["mes"]
    return await _rows(db, f"""
        SELECT {trunc} AS mes, sum(o.total_value) AS faturado
        FROM core.orders o WHERE {f.where} AND {FATURADO}
        GROUP BY {trunc} ORDER BY 1
    """, f.params)


@router.get("/status-breakdown", summary="Pedidos e valor por status canônico")
async def get_status_breakdown(
    f: OrderFilters = Depends(), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    return await _rows(db, f"""
        SELECT {STATUS_CASE} AS status, count(*) AS qtd,
               coalesce(sum(o.total_value), 0) AS valor
        FROM core.orders o WHERE {f.where}
        GROUP BY {STATUS_CASE} ORDER BY 2 DESC
    """, f.params)


@router.get("/top-customers", summary="Top clientes por valor comprado")
async def get_top_customers(
    limit: int = Query(10, ge=1, le=100),
    f: OrderFilters = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _rows(db, f"""
        SELECT TOP (:limit) o.cnpj AS cliente, count(*) AS pedidos,
               sum(o.total_value) AS valor, max(o.date) AS ultima_compra,
               avg(o.total_value) AS ticket
        FROM core.orders o WHERE {f.where}
        GROUP BY o.cnpj ORDER BY 3 DESC
    """, {**f.params, "limit": limit})


@router.get("/top-products", summary="Produtos mais vendidos por valor")
async def get_top_products(
    limit: int = Query(10, ge=1, le=100),
    f: OrderFilters = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _rows(db, f"""
        SELECT TOP (:limit) p.part_number AS pn, max(p.description) AS produto,
               sum(p.quantity) AS qtd, sum(p.quantity * p.unit_price) AS valor
        FROM core.products p
        JOIN core.orders o ON o.id = p.order_id
        WHERE {f.where}
        GROUP BY p.part_number ORDER BY 4 DESC
    """, {**f.params, "limit": limit})


@router.get("/weekday", summary="Pedidos por dia da semana (0 = domingo)")
async def get_weekday(
    f: OrderFilters = Depends(), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    # ``@@DATEFIRST`` varia com o idioma da sessão; normalizar deixa 0 = domingo
    # independentemente da configuração do servidor.
    dow = "((DATEPART(weekday, o.date) + @@DATEFIRST - 1) % 7)"
    return await _rows(db, f"""
        SELECT {dow} AS dow, count(*) AS qtd
        FROM core.orders o WHERE {f.where}
        GROUP BY {dow} ORDER BY 1
    """, f.params)


# ─────────────────────────────────────────────────────────────────────────────
# Pedidos
# ─────────────────────────────────────────────────────────────────────────────
class OrderSearch:
    """Busca livre + status + UF da página de Pedidos."""

    def __init__(
        self,
        q: Optional[str] = Query(None, description="Nº pedido Vale, CNPJ ou centro"),
        status: Optional[str] = Query(None, description="Status canônico"),
        uf: Optional[str] = Query(None),
    ) -> None:
        clauses = ["1=1"]
        params: dict[str, Any] = {}
        if q:
            clauses.append(
                "(CAST(o.vale_order_id AS varchar(32)) LIKE :q "
                "OR o.cnpj LIKE :q OR o.center LIKE :q)"
            )
            params["q"] = f"%{q}%"
        if status and status in STATUS_WHERE:
            clauses.append(f"({STATUS_WHERE[status]})")
        if uf:
            clauses.append("o.state = :uf")
            params["uf"] = uf
        self.where = " AND ".join(clauses)
        self.params = params


@router.get("/orders", summary="Lista paginada de pedidos com status canônico")
async def get_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    s: OrderSearch = Depends(),
    db: AsyncSession = Depends(get_db),
) -> dict:
    # Duas consultas em vez de COUNT(*) OVER(): numa página além do fim (offset
    # maior que o total de linhas), a janela não teria linha nenhuma para
    # carregar a contagem, e "total" viria zerado por engano.
    total = (await _row(db, f"""
        SELECT count(*) AS n FROM core.orders o WHERE {s.where}
    """, s.params))["n"]

    items = await _rows(db, f"""
        SELECT o.vale_order_id AS pedido, o.date AS data, o.cnpj AS cliente,
               o.center AS centro, o.state AS uf, o.total_value AS valor,
               {STATUS_CASE} AS status, o.invoice_number AS nf
        FROM core.orders o WHERE {s.where}
        ORDER BY o.date DESC
        OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY
    """, {**s.params, "offset": (page - 1) * page_size, "page_size": page_size})

    pages = -(-total // page_size) if total else 0  # ceil sem importar math
    return {"items": items, "total": total, "page": page, "page_size": page_size, "pages": pages}


@router.get("/orders/status-distribution", summary="Pedidos por status (filtro da página)")
async def get_orders_status(
    s: OrderSearch = Depends(), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    return await _rows(db, f"""
        SELECT {STATUS_CASE} AS status, count(*) AS qtd
        FROM core.orders o WHERE {s.where}
        GROUP BY {STATUS_CASE} ORDER BY 2 DESC
    """, s.params)


@router.get("/orders/centers", summary="Top centros por nº de pedidos")
async def get_orders_centers(
    limit: int = Query(8, ge=1, le=50),
    s: OrderSearch = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _rows(db, f"""
        SELECT TOP (:limit) o.center AS centro, count(*) AS qtd
        FROM core.orders o WHERE {s.where} AND o.center IS NOT NULL
        GROUP BY o.center ORDER BY 2 DESC
    """, {**s.params, "limit": limit})


# Etapas do fluxo do pedido, na ordem em que o BESC realmente executa:
# recebe do COUPA, cadastra no SUPRA, abre chamado só se algo precisar de
# ajuste manual, confirma e por fim fatura.
ORDER_STEPS = [
    {"key": "coupa", "label": "Extraído do COUPA"},
    {"key": "supra", "label": "Cadastrado no SUPRA"},
    {"key": "chamado", "label": "Chamado"},
    {"key": "confirmado", "label": "Confirmado"},
    {"key": "faturado", "label": "Faturado"},
]


@router.get(
    "/orders/{pedido}/timeline",
    summary="Progresso do pedido pelas etapas do workflow (para o stepper)",
)
async def get_order_timeline(pedido: int, db: AsyncSession = Depends(get_db)) -> dict:
    order = await _row(db, """
        SELECT TOP (1) o.id, o.vale_order_id, o.process_id, o.status_code,
               o.invoice_number, o.version, o.created_at, o.updated_at
        FROM core.orders o WHERE o.vale_order_id = :pedido
    """, {"pedido": pedido})
    if not order:
        raise HTTPException(status_code=404, detail=f"Pedido {pedido} não encontrado")

    # Subconsultas escalares: sempre devolvem uma linha, mesmo sem nenhum
    # registro de auditoria para o pedido (evita um segundo round-trip vazio).
    history = await _row(db, """
        SELECT
          (SELECT TOP (1) occurred_at FROM audit.process_history
            WHERE order_id = :pedido ORDER BY occurred_at) AS first_seen,
          (SELECT TOP (1) description FROM audit.process_history
            WHERE order_id = :pedido ORDER BY occurred_at) AS first_description,
          (SELECT max(occurred_at) FROM audit.process_history
            WHERE order_id = :pedido AND description LIKE 'Pedido confirmado%') AS confirmed_at
    """, {"pedido": pedido})

    tickets = await _rows(db, """
        SELECT t.ticket_number, coalesce(ts.name, CONCAT('status ', t.status_id)) AS status,
               t.opened_at, t.closed_at
        FROM support.tickets t
        LEFT JOIN support.tickets_status ts ON ts.id = t.status_id
        WHERE t.order_id = :order_id
        ORDER BY t.opened_at
    """, {"order_id": order["id"]})

    faturado = order["process_id"] == 1 and order["status_code"] == 4
    confirmado = order["process_id"] == 1 and order["status_code"] == 3
    cancelado = order["status_code"] == 5

    abertos = sum(1 for t in tickets if t["status"] == "EM_ANDAMENTO")
    if not tickets:
        ticket_state = "none"
    elif abertos:
        ticket_state = "andamento"
    else:
        ticket_state = "concluido"

    # Estado por etapa. O pedido só tem UM ponto "current" — a frente de onda
    # do fluxo — computado a partir do status canônico, não etapa por etapa
    # isoladamente (evita duas etapas "em andamento" ao mesmo tempo).
    states = {"coupa": "done", "supra": "done", "chamado": "pending",
              "confirmado": "pending", "faturado": "pending"}

    chamado_done_or_skipped = "done" if tickets else "skipped"

    if faturado:
        states["chamado"] = chamado_done_or_skipped
        states["confirmado"] = "done"
        states["faturado"] = "done"
    elif confirmado:
        states["chamado"] = chamado_done_or_skipped
        states["confirmado"] = "done"
        states["faturado"] = "current"
    else:
        # Aguardando processamento: a frente de onda para no chamado aberto,
        # se houver um; senão já está esperando confirmação.
        if ticket_state == "andamento":
            states["chamado"] = "current"
        else:
            states["chamado"] = chamado_done_or_skipped
            states["confirmado"] = "current"

    if cancelado:
        # O pedido parou — nada está "em andamento" de fato. Mostra só o que
        # objetivamente aconteceu; não inventa em qual etapa exata foi
        # cancelado, já que o histórico não registra esse evento.
        states = {k: ("pending" if v == "current" else v) for k, v in states.items()}

    last_ticket = tickets[-1] if tickets else None
    at_map = {
        "coupa": history.get("first_seen") or order["created_at"],
        "supra": order["created_at"],
        "chamado": (last_ticket and (last_ticket["closed_at"] or last_ticket["opened_at"])),
        "confirmado": history.get("confirmed_at")
        or (order["updated_at"] if confirmado or faturado else None),
        "faturado": order["updated_at"] if faturado else None,
    }

    def ticket_detail() -> str | None:
        if not tickets:
            return None
        plural = "s" if len(tickets) != 1 else ""
        detail = f"{len(tickets)} chamado{plural}"
        if abertos:
            detail += f" · {abertos} em andamento"
        return detail

    detail_map = {
        "coupa": history.get("first_description"),
        "supra": f"versão {order['version']}" if order.get("version") else None,
        "chamado": ticket_detail(),
        "confirmado": None,
        "faturado": f"NF {order['invoice_number']}" if order.get("invoice_number") else None,
    }

    status_label = (
        "Concretizado" if faturado
        else "Cancelada" if cancelado
        else "Confirmado" if confirmado
        else "Aguardando Processamento"
    )

    return {
        "pedido": order["vale_order_id"],
        "status": status_label,
        "cancelado": cancelado,
        "atualizado_em": order["updated_at"],
        "steps": [
            {
                "key": step["key"],
                "label": step["label"],
                "state": states[step["key"]],
                "at": at_map[step["key"]],
                "detail": detail_map[step["key"]],
            }
            for step in ORDER_STEPS
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Financeiro
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/finance/summary", summary="Faturado x pipeline x cancelado")
async def get_finance_summary(db: AsyncSession = Depends(get_db)) -> dict:
    return await _row(db, """
        SELECT
          coalesce(sum(CASE WHEN process_id = 1 AND status_code = 4
                            THEN total_value END), 0) AS faturado,
          coalesce(sum(CASE WHEN NOT (process_id = 1 AND status_code = 4)
                             AND (status_code IS NULL OR status_code <> 5)
                            THEN total_value END), 0) AS pipeline,
          coalesce(sum(CASE WHEN status_code = 5 THEN total_value END), 0) AS cancelado,
          coalesce(sum(total_value), 0) AS total
        FROM core.orders
    """)


@router.get("/finance/status-value", summary="Composição do valor por status")
async def get_finance_status_value(db: AsyncSession = Depends(get_db)) -> list[dict]:
    return await _rows(db, f"""
        SELECT {STATUS_CASE} AS status, coalesce(sum(o.total_value), 0) AS valor
        FROM core.orders o
        GROUP BY {STATUS_CASE} ORDER BY 2 DESC
    """)


@router.get("/finance/by-state", summary="Faturado x pipeline por filial (UF)")
async def get_finance_by_state(db: AsyncSession = Depends(get_db)) -> list[dict]:
    return await _rows(db, """
        SELECT state AS uf,
               coalesce(sum(CASE WHEN process_id = 1 AND status_code = 4
                                 THEN total_value END), 0) AS faturado,
               coalesce(sum(CASE WHEN NOT (process_id = 1 AND status_code = 4)
                                  AND (status_code IS NULL OR status_code <> 5)
                                 THEN total_value END), 0) AS pipeline
        FROM core.orders WHERE state IS NOT NULL
        GROUP BY state ORDER BY 2 DESC
    """)


@router.get("/finance/by-center", summary="Pedidos e valor por centro")
async def get_finance_by_center(
    limit: int = Query(12, ge=1, le=100), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    return await _rows(db, """
        SELECT TOP (:limit) center AS centro, count(*) AS pedidos,
               sum(total_value) AS valor
        FROM core.orders WHERE center IS NOT NULL
        GROUP BY center ORDER BY 3 DESC
    """, {"limit": limit})


@router.get("/finance/monthly", summary="Faturamento mensal (série completa)")
async def get_finance_monthly(db: AsyncSession = Depends(get_db)) -> list[dict]:
    return await _rows(db, """
        SELECT CAST(DATEADD(month, DATEDIFF(month, 0, date), 0) AS date) AS mes,
               sum(total_value) AS faturado
        FROM core.orders WHERE process_id = 1 AND status_code = 4
        GROUP BY DATEADD(month, DATEDIFF(month, 0, date), 0) ORDER BY 1
    """)


# ─────────────────────────────────────────────────────────────────────────────
# Chamados
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/tickets/summary", summary="KPIs de chamados")
async def get_tickets_summary(db: AsyncSession = Depends(get_db)) -> dict:
    return await _row(db, """
        SELECT count(*) AS total,
               count(CASE WHEN status_id = 2 THEN 1 END) AS concluidos,
               count(CASE WHEN status_id IN (0,1,3) THEN 1 END) AS abertos,
               (SELECT count(*) FROM support.ticket_divergences) AS divergencias
        FROM support.tickets
    """)


@router.get("/tickets/by-status", summary="Chamados por status")
async def get_tickets_by_status(db: AsyncSession = Depends(get_db)) -> list[dict]:
    expr = "coalesce(ts.name, CONCAT('status ', t.status_id))"
    return await _rows(db, f"""
        SELECT {expr} AS status, count(*) AS qtd
        FROM support.tickets t
        LEFT JOIN support.tickets_status ts ON ts.id = t.status_id
        GROUP BY {expr} ORDER BY 2 DESC
    """)


@router.get("/tickets/progress-funnel", summary="Etapas mais percorridas")
async def get_tickets_funnel(
    limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    expr = "coalesce(sp.name, CONCAT('etapa ', tp.status_progress_id))"
    return await _rows(db, f"""
        SELECT TOP (:limit) {expr} AS etapa, count(*) AS qtd
        FROM support.ticket_progresses tp
        LEFT JOIN support.status_progress sp ON sp.id = tp.status_progress_id
        GROUP BY {expr} ORDER BY 2 DESC
    """, {"limit": limit})


@router.get("/tickets", summary="Lista paginada de chamados, com busca por chamado ou pedido")
async def get_tickets(
    q: Optional[str] = Query(None, description="Nº do chamado ou do pedido"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> dict:
    clauses = ["1=1"]
    params: dict[str, Any] = {}
    if q:
        clauses.append(
            "(CAST(t.ticket_number AS varchar(32)) LIKE :q "
            "OR CAST(t.purchase_order AS varchar(32)) LIKE :q)"
        )
        params["q"] = f"%{q}%"
    where = " AND ".join(clauses)

    total = (await _row(db, f"""
        SELECT count(*) AS n FROM support.tickets t WHERE {where}
    """, params))["n"]

    items = await _rows(db, f"""
        SELECT t.ticket_number AS ticket, t.purchase_order AS pedido,
               coalesce(ts.name, CONCAT('status ', t.status_id)) AS status,
               t.opened_at AS aberto_em, t.closed_at AS fechado_em
        FROM support.tickets t
        LEFT JOIN support.tickets_status ts ON ts.id = t.status_id
        WHERE {where}
        ORDER BY t.opened_at DESC, t.id DESC
        OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY
    """, {**params, "offset": (page - 1) * page_size, "page_size": page_size})

    pages = -(-total // page_size) if total else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "pages": pages}


@router.get(
    "/tickets/{ticket_number}/timeline",
    summary="Progresso de um chamado pelas etapas realmente percorridas",
)
async def get_ticket_timeline(ticket_number: int, db: AsyncSession = Depends(get_db)) -> dict:
    ticket = await _row(db, """
        SELECT TOP (1) t.id, t.ticket_number AS ticket, t.purchase_order AS pedido,
               coalesce(ts.name, CONCAT('status ', t.status_id)) AS status,
               t.opened_at, t.closed_at
        FROM support.tickets t
        LEFT JOIN support.tickets_status ts ON ts.id = t.status_id
        WHERE t.ticket_number = :ticket_number
    """, {"ticket_number": ticket_number})
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Chamado {ticket_number} não encontrado")

    # ``start_date`` tem granularidade de dia (muitas etapas empatam) e não dá
    # pra confiar nele pra ordenar. ``id`` resolve isso: a extração grava o
    # histórico de um chamado inteiro num lote só, do evento mais recente pro
    # mais antigo — id crescente = created_at crescente = evento mais antigo
    # tem o MAIOR id. ``ORDER BY id DESC`` é a ordem cronológica real.
    steps = await _rows(db, """
        SELECT coalesce(sp.name, CONCAT('etapa ', tp.status_progress_id)) AS etapa,
               tp.start_date AS inicio, tp.end_date AS fim
        FROM support.ticket_progresses tp
        LEFT JOIN support.status_progress sp ON sp.id = tp.status_progress_id
        WHERE tp.ticket_id = :ticket_id
        ORDER BY tp.id DESC
    """, {"ticket_id": ticket["id"]})

    return {
        "ticket": ticket["ticket"],
        "pedido": ticket["pedido"],
        "status": ticket["status"],
        "opened_at": ticket["opened_at"],
        "closed_at": ticket["closed_at"],
        "steps": steps,
    }


@router.get("/tickets/divergences", summary="Pedidos com mais divergências")
async def get_tickets_divergences(
    limit: int = Query(15, ge=1, le=100), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    return await _rows(db, """
        SELECT TOP (:limit) t.purchase_order AS pedido, t.ticket_number AS ticket,
               count(*) AS divergencias
        FROM support.ticket_divergences d
        JOIN support.tickets t ON t.id = d.ticket_id
        GROUP BY t.purchase_order, t.ticket_number ORDER BY 3 DESC
    """, {"limit": limit})


# ─────────────────────────────────────────────────────────────────────────────
# Compras & Estoque
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/inventory/summary", summary="KPIs de itens e solicitações de compra")
async def get_inventory_summary(db: AsyncSession = Depends(get_db)) -> dict:
    itens = await _row(db, """
        SELECT count(*) AS itens,
               coalesce(sum(quantity * unit_price), 0) AS valor_total
        FROM core.products
    """)
    pr = await _row(db, """
        SELECT count(CASE WHEN status = 'PENDING' THEN 1 END) AS pendentes,
               count(CASE WHEN status = 'COMPLETED' THEN 1 END) AS concluidas
        FROM purchasing.purchase_requests
    """)
    return {**itens, **pr}


@router.get("/inventory/by-status", summary="Itens por situação de estoque")
async def get_inventory_by_status(db: AsyncSession = Depends(get_db)) -> list[dict]:
    expr = "coalesce(ss.name, CONCAT('status ', p.stock_status_id))"
    return await _rows(db, f"""
        SELECT {expr} AS status, count(*) AS qtd,
               coalesce(sum(p.quantity * p.unit_price), 0) AS valor
        FROM core.products p
        LEFT JOIN core.stock_status ss ON ss.id = p.stock_status_id
        GROUP BY {expr} ORDER BY 2 DESC
    """)


@router.get("/inventory/purchase-requests", summary="Solicitações de compra")
async def get_purchase_requests(
    limit: int = Query(50, ge=1, le=500), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    # Faltante = Solicitado − Liberado, nunca negativo — é a mesma regra que
    # define o status (COMPLETED quando liberado >= solicitado), então nas
    # linhas concluídas o faltante é sempre 0.
    return await _rows(db, """
        SELECT TOP (:limit)
               order_id AS pedido, part_number AS pn,
               released_quantity AS liberado, requested_quantity AS solicitado,
               GREATEST(requested_quantity - released_quantity, 0) AS faltante,
               status,
               DATEDIFF(day, created_at, SYSDATETIMEOFFSET()) AS dias
        FROM purchasing.purchase_requests
        ORDER BY created_at DESC
    """, {"limit": limit})


# ─────────────────────────────────────────────────────────────────────────────
# Produtos & Preços
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/products/summary", summary="KPIs do catálogo")
async def get_products_summary(db: AsyncSession = Depends(get_db)) -> dict:
    return await _row(db, """
        SELECT (SELECT count(*) FROM pricing.prices) AS catalogo,
               (SELECT count(DISTINCT part_number) FROM core.products) AS vendidos,
               (SELECT count(*) FROM pricing.prices WHERE destination = 'MG') AS mg,
               (SELECT count(*) FROM pricing.prices WHERE destination = 'PA') AS pa
    """)


@router.get("/products/top", summary="Produtos mais vendidos (valor)")
async def get_products_top(
    limit: int = Query(15, ge=1, le=100), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    return await _rows(db, """
        SELECT TOP (:limit) part_number AS pn, max(description) AS produto,
               sum(quantity) AS qtd, sum(quantity * unit_price) AS valor
        FROM core.products
        GROUP BY part_number ORDER BY 4 DESC
    """, {"limit": limit})


@router.get("/products/abc", summary="Curva ABC por valor vendido")
async def get_products_abc(db: AsyncSession = Depends(get_db)) -> list[dict]:
    classe = "CASE WHEN acum <= 0.8 THEN 'A' WHEN acum <= 0.95 THEN 'B' ELSE 'C' END"
    return await _rows(db, f"""
        WITH v AS (
          SELECT part_number, sum(quantity * unit_price) AS valor
          FROM core.products GROUP BY part_number
        ), r AS (
          SELECT part_number, valor,
                 sum(valor) OVER (ORDER BY valor DESC)
                   / NULLIF(sum(valor) OVER (), 0) AS acum
          FROM v
        )
        SELECT {classe} AS classe, count(*) AS qtd, sum(valor) AS valor
        FROM r GROUP BY {classe} ORDER BY 1
    """)


@router.get("/products/search", summary="Busca no catálogo por PN ou descrição")
async def search_products(
    q: str = Query(..., min_length=1),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    # A collation do banco é CI (Latin1_General_CI_AS): LIKE já é
    # case-insensitive, equivalente ao ILIKE do Postgres.
    return await _rows(db, """
        SELECT TOP (:limit) pn, description AS descricao,
               destination AS destino, unit_price AS preco
        FROM pricing.prices
        WHERE pn LIKE :q OR description LIKE :q OR long_description LIKE :q
        ORDER BY pn
    """, {"q": f"%{q}%", "limit": limit})
