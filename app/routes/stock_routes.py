from fastapi import APIRouter, Request
from app.models.predict_request import PredictRequest
from app.services.stock_service import fetch_stock_data, get_stock_history_data
import os
from fastapi import HTTPException

router = APIRouter(prefix="/api/stocks", tags=["Stock"])

@router.get("/{symbol}")
async def get_stock_history(
    symbol: str,
    interval: str = "1d",  # Bisa diganti frontend (misal 1d, 1wk, 1mo)
):
    if not symbol.isalpha():
        raise HTTPException(status_code=400, detail="Invalid stock symbol")

    try:
        data = await get_stock_history_data(symbol=symbol, interval=interval)
        return {"symbol": symbol.upper(), "interval": interval, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{symbol}")
async def get_stock_prediction(symbol: str, request: Request):
    redis = request.app.state.redis
    model = request.app.state.stock_model
    return await fetch_stock_data(symbol, redis, model, request)