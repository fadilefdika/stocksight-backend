from fastapi import APIRouter, Request
from app.models.predict_request import PredictRequest
from app.services.stock_service import fetch_stock_data, get_stock_history_data
import os
from fastapi import HTTPException

router = APIRouter(prefix="/api/stocks", tags=["Stock"])

@router.get("/{symbol}")
async def get_stock_history(
    symbol: str,
    interval: str = "1d",     # Contoh: 1d, 1wk, 1mo
    period: str = "1mo"       # Contoh: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
):
    if not symbol.isalpha():
        raise HTTPException(status_code=400, detail="Invalid stock symbol")

    try:
        data = await get_stock_history_data(symbol=symbol, interval=interval, period=period)
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "period": period,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict/{symbol}")
async def get_stock_prediction(symbol: str, request: Request):
    redis = request.app.state.redis
    model = request.app.state.stock_model
    return await fetch_stock_data(symbol, redis, model, request)