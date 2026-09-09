# app/main.py
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa rotas
from app.core.security import jwt_middleware
from app.api.routers.dashboard import router as router_dashboard
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
from app.api.routers.fiscal_notifications import router as router_fiscal_notifications
from app.api.routers.invoices import router as router_invoices
from app.api.middlewares.exception_handlers import register_exception_handlers
#
from app.database import init_db

# Cria instância principal da aplicação.
#
# Docs e schema ficam sob /api porque o IIS serve o dashboard React na raiz do
# mesmo site (porta 9579): "/" é do React, "/api" é desta API. Nos caminhos
# padrão (/docs, /openapi.json) quem responderia seria o dashboard.
#
# Não definir root_path="/api": o httpPlatformHandler encaminha o caminho
# completo, incluindo /api, e os routers já carregam esse prefixo — o root_path
# duplicaria para /api/api/...
app = FastAPI(
    title="User Auth API",
    description="API de autenticação e gerenciamento de usuários",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    swagger_ui_oauth2_redirect_url="/api/docs/oauth2-redirect",
)

app.middleware("http")(jwt_middleware)

# O dashboard React roda em outra origem (Vite). O CORS é adicionado DEPOIS do
# jwt_middleware de propósito: no Starlette o último middleware registrado fica
# por fora, então o preflight OPTIONS é respondido sem passar pela checagem de
# token — e o 401 de token ausente volta com os headers de CORS, permitindo que
# o navegador leia a resposta em vez de reportar um erro de rede genérico.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5174,http://127.0.0.1:5174,http://besc-orders-api.defenseti.com.br:9579",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(router_fiscal_notifications, tags=["Fiscal Notifications"])
app.include_router(router_invoices, tags=["Invoices"])
app.include_router(router_dashboard, tags=["Dashboard"])



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
    # Sem emoji nas mensagens: sob o IIS o stdout usa cp1252 e qualquer
    # caractere fora dessa tabela levanta UnicodeEncodeError, derrubando o
    # startup inteiro.
    if os.getenv("RUN_DB_CREATE_ALL", "false").lower() == "true":
        await init_db()
        print("Banco de dados inicializado (create_all).")
    else:
        print("Startup sem create_all (schema gerenciado pelo Alembic).")


@app.on_event("shutdown")
async def on_shutdown():
    """Executa ao encerrar a aplicação."""
    print("Encerrando aplicacao...")
