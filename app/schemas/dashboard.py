from pydantic import BaseModel
from typing import List
from datetime import datetime


class RiskDistribution(BaseModel):
    low: int
    medium: int
    high: int


class RecentAnalysis(BaseModel):
    id: int
    original_text: str
    summary_score: int
    overall_risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_analyses: int
    risk_distribution: RiskDistribution
    recent_analyses: List[RecentAnalysis]
    average_score: float
