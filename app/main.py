# app/main.py
import os

from fastapi import FastAPI

# Importa rotas
from app.core.security import jwt_middleware
from app.api.routers.orders import router as router_orders
from app.api.routers.products import router as router_products
from app.api.routers.auth import router as router_auth
from app.api.routers.price_table import router as router_price_table
from app.api.routers.history_process import router as router_history_process
from app.api.routers.tickets import router as router_tickets
from app.api.routers.ticket_progresses import router as router_ticket_progress
from app.api.routers.ticket_divergences import router as router_ticket_divergence
from app.api.routers.tax_reference import router as router_tax_reference
from app.api.routers.purchase_requests import router as router_purchase_requests
from app.api.routers.invoices import router as router_invoices
from app.api.middlewares.exception_handlers import register_exception_handlers

from app.database import init_db

# Cria instância principal da aplicação
app = FastAPI(
    title="User Auth API",
    description="API de autenticação e gerenciamento de usuários",
    version="1.0.0",
)

app.middleware("http")(jwt_middleware)

# Standardized error responses for domain/application exceptions
register_exception_handlers(app)

# Inclui rotas registradas
app.include_router(router_orders, tags=["Orders"])
app.include_router(router_products, tags=["Products"])
app.include_router(router_auth, tags=["Authentication"])
app.include_router(router_price_table, tags=["Price Table"])
app.include_router(router_history_process, tags=["History Process"])
app.include_router(router_tickets, tags=["Tickets"])
app.include_router(router_ticket_progress, tags=["Ticket Progress"])
app.include_router(router_ticket_divergence, tags=["Ticket Divergence"])
app.include_router(router_tax_reference, tags=["Tax Reference"])
app.include_router(router_purchase_requests, tags=["Purchase Requests"])
app.include_router(router_invoices, tags=["Invoices"])



# ====================================
# EVENTOS DE CICLO DE VIDA DO FASTAPI
# ====================================
@app.on_event("startup")
async def on_startup():
    """Executa ao iniciar a aplicação.

    O schema é gerenciado pelo Alembic. O ``create_all`` fica desligado por
    padrão (evita corrida entre instâncias no Cloud Run) e só roda quando
    ``RUN_DB_CREATE_ALL=true`` — útil para desenvolvimento local.
    """
    if True:
        await init_db()
        print("✅ Banco de dados inicializado (create_all).")
    else:
        print("ℹ️  Startup sem create_all (schema gerenciado pelo Alembic).")


@app.on_event("shutdown")
async def on_shutdown():
    """Executa ao encerrar a aplicação."""
    print("🛑 Encerrando aplicação...")
