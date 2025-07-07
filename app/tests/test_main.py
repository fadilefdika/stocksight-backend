from fastapi.testclient import TestClient
from app.main import app
from app.services.stock_service import add_stock, get_stock
from datetime import datetime


client = TestClient(app)

def test_add_stock():
    stock_data = {
        "symbol": "LSTM",
        "company_name": "Alphabet Inc.",
        "sector": "SUAWU",
        "industry": "Internet",
        "price_history": [
            {
                "date": datetime(2023, 1, 1),
                "open": 1500.0,
                "close": 1550.0,
                "high": 1560.0,
                "low": 1495.0,
                "volume": 1000000
            }
        ]
    }
    response = add_stock(stock_data)
    assert response is not None

def test_get_stock():
    stock = get_stock("GOOGL")
    assert stock.symbol == "GOOGL"
