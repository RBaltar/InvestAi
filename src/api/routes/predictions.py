from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from sqlalchemy import text

router = APIRouter()

@router.get("/{ticker}")
def get_predictions(ticker: str, db: Session = Depends(get_db)):
    query = text(f"SELECT date, predicted_price FROM acoes_previsoes WHERE ticker = '{ticker}' ORDER BY date ASC")
    predictions = db.execute(query).fetchall()

    if not predictions:
        raise HTTPException(status_code=404, detail="Nenhuma previsão encontrada para este ticker")

    return {"ticker": ticker, "predictions": [{"date": p[0], "predicted_price": p[1]} for p in predictions]}
