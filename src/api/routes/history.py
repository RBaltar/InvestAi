from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from sqlalchemy import text

router = APIRouter()

@router.get("/{ticker}")
def get_history(ticker: str, db: Session = Depends(get_db)):
    query = text(f"SELECT date, close FROM acoes_historico WHERE ticker = '{ticker}' ORDER BY date ASC")
    history = db.execute(query).fetchall()

    if not history:
        raise HTTPException(status_code=404, detail="Ticker não encontrado")

    return {"ticker": ticker, "history": [{"date": h[0], "close": h[1]} for h in history]}
