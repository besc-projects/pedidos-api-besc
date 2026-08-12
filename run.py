import uvicorn

# ====================================
# PONTO DE ENTRADA
# ====================================
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,  # Recarrega automaticamente durante o desenvolvimento
    )
