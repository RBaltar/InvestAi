from fastapi import FastAPI
from api.routes import tickers, history, predictions, comparison

app = FastAPI(title="InvestAI API", description="API para acessar dados de ações e previsões", version="1.0")

# Importa os módulos de rotas
app.include_router(tickers.router, prefix="/tickers", tags=["Tickers"])
app.include_router(history.router, prefix="/history", tags=["Histórico"])
app.include_router(predictions.router, prefix="/predictions", tags=["Previsões"])
app.include_router(comparison.router, prefix="/comparison", tags=["Comparação"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "🚀 InvestAI API está rodando!"}
