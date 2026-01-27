# app/main.py
from fastapi import FastAPI

# Importa rotas
from app.core.security import jwt_middleware
from app.routers.orders import router as router_orders
from app.routers.products import router as router_products
from app.routers.auth import router as router_auth
from app.routers.taxes import router as router_tax
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
app.include_router(router_auth, tags=["Authentication"])
app.include_router(router_tax, tags=["Tax"])


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
