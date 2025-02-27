from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.database import get_db
from sqlalchemy import text

router = APIRouter()

@router.get("/")
def get_tickers(db: Session = Depends(get_db)):
    query = text("SELECT DISTINCT ticker FROM acoes_historico")
    tickers = db.execute(query).fetchall()
    
    return {"tickers": [t[0] for t in tickers]}
