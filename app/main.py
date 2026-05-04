# app/main.py
from fastapi import FastAPI

# Importa rotas
from app.core.security import jwt_middleware
from app.routers.orders import router as router_orders
from app.routers.products import router as router_products
from app.routers.proposals import router as router_proposals
from app.routers.auth import router as router_auth
from app.routers.price_table import router as router_price_table
from app.routers.history_process import router as router_history_process
from app.routers.tickets import router as router_tickets
from app.routers.ticket.progress import router as router_ticket_progress
from app.routers.ticket.divergence import router as router_ticket_divergence
from app.routers.tax_reference import router as router_tax_reference

from app.database import init_db

# Cria instância principal da aplicação
app = FastAPI(
    title="User Auth API",
    description="API de autenticação e gerenciamento de usuários",
    version="1.0.0",
)

app.middleware("http")(jwt_middleware)

# Inclui rotas registradas
app.include_router(router_orders, tags=["Orders"])
app.include_router(router_products, tags=["Products"])
app.include_router(router_proposals, tags=["Proposals"])
app.include_router(router_auth, tags=["Authentication"])
app.include_router(router_price_table, tags=["Price Table"])
app.include_router(router_history_process, tags=["History Process"])
app.include_router(router_tickets, tags=["Tickets"])
app.include_router(router_ticket_progress, tags=["Ticket Progress"])
app.include_router(router_ticket_divergence, tags=["Ticket Divergence"])
app.include_router(router_tax_reference, tags=["Tax Reference"])



# ====================================
# EVENTOS DE CICLO DE VIDA DO FASTAPI
# ====================================
@app.on_event("startup")
async def on_startup():
    """Executa ao iniciar a aplicação."""
    await init_db()  # Cria as tabelas se ainda não existirem
    print("✅ Banco de dados inicializado com sucesso!")


@app.on_event("shutdown")
async def on_shutdown():
    """Executa ao encerrar a aplicação."""
    print("🛑 Encerrando aplicação...")
