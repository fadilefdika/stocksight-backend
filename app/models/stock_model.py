# app/models/stock_model.py
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

class Stock(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id")
    symbol: str
    company_name: str
    historical_data: List[dict]  # Format bebas: {date: str, close: float, ...}

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
