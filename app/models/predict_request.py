from pydantic import BaseModel
from typing import List

class PredictRequest(BaseModel):
    input_data: List[float]
