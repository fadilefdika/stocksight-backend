# app/models/prediction_model.py
from pydantic import BaseModel
from datetime import date
from typing import Literal

class PredictionModel(BaseModel):
    symbol: str
    date: date
    predicted_close: float
    confidence: float
    prediction_type: Literal["lstm", "linear", "random_forest"]  # Contoh jika kamu punya banyak tipe prediksi
