import joblib
from fastapi import FastAPI
from app.routes import stock_routes
from dotenv import load_dotenv
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os

# Tambahkan import model
from tensorflow.keras.models import load_model

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load scaler
    scaler = joblib.load("models/scaler.pkl")

    # Load model
    model_path = os.getenv("STOCK_MODEL_PATH", "models/stock_lstm_model.keras")
    try:
        stock_model = load_model(model_path, compile=False)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load model from {model_path}: {e}")

    # Connect Redis
    redis = await aioredis.from_url("redis://localhost")

    # Simpan ke app state
    app.state.scaler = scaler
    app.state.stock_model = stock_model
    app.state.redis = redis

    # Jalankan aplikasi
    yield

    # Cleanup
    await redis.close()
    await redis.connection_pool.disconnect()

# Inisialisasi FastAPI dengan lifespan
app = FastAPI(lifespan=lifespan)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(stock_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock Prediction API"}