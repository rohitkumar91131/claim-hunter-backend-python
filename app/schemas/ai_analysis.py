from pydantic import BaseModel, Field, conint
from typing import List, Literal

class ClaimResult(BaseModel):
    claim: str
    verdict: Literal["True", "Likely True", "Uncertain", "Likely False", "False"]
    fact_check_probability: conint(ge=0, le=100)
    confidence: conint(ge=0, le=100)
    reasoning: str

class AIAnalysisResponse(BaseModel):
    summary_score: conint(ge=0, le=100)
    overall_risk_level: Literal["Low", "Medium", "High"]
    claims: List[ClaimResult]
    emotional_tone: Literal["Neutral", "Emotional", "Manipulative", "Fear-Based", "Conspiratorial"]
    manipulation_score: conint(ge=0, le=100)
    confidence_overall: conint(ge=0, le=100)
