from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    text: str

class AnalysisCreate(BaseModel):
    original_text: str
    result: Dict[str, Any]

class AnalysisResponse(BaseModel):
    id: int
    user_id: int
    original_text: str
    result: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
