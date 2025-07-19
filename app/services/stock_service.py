from datetime import datetime, timedelta
from fastapi import HTTPException, Request,Query
import json
import traceback
import numpy as np
import yfinance as yf

VALID_PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
VALID_INTERVALS = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo", "3mo"]

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

    # Tambahkan indikator teknikal
    hist = add_technical_indicators(hist)

    # Pastikan semua kolom ada & tanpa NaN
    required_features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA', 'EMA', 'RSI']
    hist = hist[required_features].dropna()

    if len(hist) < 60:
        raise HTTPException(status_code=400, detail="Not enough clean data after indicators")

    latest_date = hist.index[-1].date()
    last_60 = hist.values[-60:]

    # Scale and reshape input
    scaled_input = scaler.transform(last_60)
    input_array = np.array(scaled_input).reshape(1, 60, len(required_features))

    future_days = 5
    predicted_results = []

    try:
        for i in range(future_days):
            prediction = model.predict(input_array)
            pred_scaled = prediction[0][0]  # asumsi prediksi hanya untuk 'Close'

            # Invers transform hanya nilai close
            dummy = np.zeros((1, len(required_features)))
            close_idx = required_features.index("Close")
            dummy[0][close_idx] = pred_scaled
            inversed = scaler.inverse_transform(dummy)
            predicted_close = float(inversed[0][close_idx])

            prediction_date = latest_date + timedelta(days=i + 1)
            predicted_results.append({
                "date": prediction_date.strftime("%Y-%m-%d"),
                "open": 0,
                "high": 0,
                "low": 0,
                "close": round(predicted_close, 2),
                "volume": 0,
                "predicted": True
            })

            # Rolling update: hanya update fitur "Close"
            next_input = np.zeros((1, len(required_features)))
            next_input[0][close_idx] = pred_scaled
            scaled_input = np.append(scaled_input[1:], next_input, axis=0)
            input_array = scaled_input.reshape(1, 60, len(required_features))

    except Exception as e:
        print("❌ Prediction error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Prediction failed")

    # Cache
    await redis.set(symbol, json.dumps(predicted_results), ex=3600)
    return predicted_results

async def get_stock_history_data(
    symbol: str = Query("AAPL", min_length=1, max_length=10),
    period: str = Query("6mo", enum=VALID_PERIODS),
    interval: str = Query("1d", enum=VALID_INTERVALS),
):
    # Validasi kombinasi period-interval
    if period in ["ytd", "max"] and interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m"]:
        raise HTTPException(status_code=400, detail="Intraday intervals are not supported for large periods like 'max' or 'ytd'.")

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for {symbol} with period={period} and interval={interval}.")

        hist.reset_index(inplace=True)
        hist['Date'] = hist['Date'].astype(str)  # agar bisa di-serialize

        result = [
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
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")



def add_technical_indicators(df):
    df = df.copy()
    df['SMA'] = df['Close'].rolling(window=14).mean()
    df['EMA'] = df['Close'].ewm(span=14, adjust=False).mean()

    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df