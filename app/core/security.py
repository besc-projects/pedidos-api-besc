import hashlib
import os
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta

from fastapi import Request
from jwt import decode, exceptions
from dotenv import load_dotenv

load_dotenv()

# Prefer JWT_SECRET (valid env var name for Cloud Run); fall back to the legacy
# dotted name for local .env backward compatibility.
JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("JWT.SECRET")
JWT_ALGORITHM: str = "HS256"


def hash_password(password: str) -> str:
    """Gera hash SHA256 para armazenar a senha com segurança."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Compara senha fornecida com hash armazenado."""
    return hash_password(password) == password_hash


def create_access_token(subject: str) -> str:
    """Cria um token JWT com validade de 12 horas."""

    payload = {"sub": subject, "exp": datetime.utcnow() + timedelta(hours=12)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str):
    """Decodifica o token JWT e retorna o payload."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


EXCLUDED_PATHS = [
    "/api/users/register",
    "/api/users/login",
    "/docs",
    "/openapi.json",
    "/health",
]


async def jwt_middleware(request: Request, call_next):
    """Middleware que exige JWT em todas as rotas (exceto as públicas)."""
    if any(request.url.path.startswith(path) for path in EXCLUDED_PATHS):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # Nao ecoar headers/token na resposta: alem de nao ajudar o cliente,
        # devolvia o proprio Authorization para quem chamou.
        return JSONResponse(
            status_code=401,
            content={"detail": "Token ausente ou inválido"},
        )

    token = auth_header.split(" ")[1]

    try:
        payload = decode(token, JWT_SECRET, algorithms=["HS256"])
    except exceptions.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"detail": "Token expirado"})
    except exceptions.DecodeError:
        return JSONResponse(status_code=401, content={"detail": "Token inválido"})
    except Exception as e:
        return JSONResponse(
            status_code=401, content={"detail": f"Erro no token: {str(e)}"}
        )

    # O payload precisa ficar disponivel para as rotas: GET /api/users/me le
    # request.state.user, que antes nunca era atribuido (resultava em 500).
    request.state.user = payload

    response = await call_next(request)
    return response
