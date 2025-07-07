from datetime import datetime, timedelta
from fastapi import HTTPException, Request
import json
import traceback
import numpy as np
import yfinance as yf

async def fetch_stock_data(symbol: str, redis, model, request: Request):
    scaler = request.app.state.scaler

    # Check Redis cache
    cached_data = await redis.get(symbol)
    if cached_data:
        return json.loads(cached_data)

    # Fetch from yfinance
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="90d")
    if hist.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    if len(hist) < 60:
        raise HTTPException(status_code=400, detail="Not enough data to predict")

    # Get last data
    latest = hist.iloc[-1]
    latest_date = latest.name.date()

    # Predict
    try:
        features = ["Open", "High", "Low", "Close", "Volume"]
        last_60 = hist[features].values[-60:]
        scaled_input = scaler.transform(last_60)
        input_array = np.array(scaled_input).reshape(1, 60, 5)

        prediction = model.predict(input_array)
        pred_scaled = prediction[0][0]

        # Inverse only "close"
        dummy = np.zeros((1, 5))
        dummy[0][3] = pred_scaled
        inversed = scaler.inverse_transform(dummy)
        predicted_close = float(inversed[0][3])

    except Exception as e:
        print("❌ Prediction error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Prediction failed")

    # Prediction date
    prediction_date = latest_date + timedelta(days=1)

    # Format result (for chart use)
    result = [
        {
            "date": prediction_date.strftime("%Y-%m-%d"),
            "open": 0,
            "high": 0,
            "low": 0,
            "close": round(predicted_close, 2),
            "volume": 0,
            "predicted": True
        }
    ]

    # Cache
    await redis.set(symbol, json.dumps(result), ex=3600)
    return result



async def get_stock_history_data(symbol: str = "AAPL", period: str = "max", interval: str = "1d"):
    ticker = yf.Ticker(symbol)

    hist = ticker.history(period=period, interval=interval)

    if hist.empty:
        raise HTTPException(status_code=404, detail="No historical data found.")

    hist.reset_index(inplace=True)
    hist['Date'] = hist['Date'].astype(str)  # pastikan bisa di-serialize JSON

    return [
        {
            "date": row["Date"],
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        }
        for _, row in hist.iterrows()
    ]