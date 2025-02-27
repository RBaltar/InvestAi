from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from sqlalchemy import text

router = APIRouter()

@router.get("/{ticker}")
def get_comparison(ticker: str, db: Session = Depends(get_db)):
    query = text(f"""
        SELECT date, predicted_price, real_price 
        FROM acoes_previsoes 
        WHERE ticker = '{ticker}' ORDER BY date ASC
    """)
    comparison = db.execute(query).fetchall()

    if not comparison:
        raise HTTPException(status_code=404, detail="Nenhuma comparação encontrada para este ticker")

    return {
        "ticker": ticker,
        "comparison": [{"date": c[0], "predicted_price": c[1], "real_price": c[2]} for c in comparison]
    }
