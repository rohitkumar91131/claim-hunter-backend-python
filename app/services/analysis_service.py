from sqlalchemy.orm import Session
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate
from app.schemas.ai_analysis import AIAnalysisResponse
from app.services.gemini_client import GeminiClient
from typing import List
from fastapi import HTTPException

class AnalysisService:

    @staticmethod
    async def perform_ai_analysis(text: str) -> AIAnalysisResponse:
        """
        Performs fully AI-driven analysis.
        Removes all local heuristics.
        """
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty")
        
        if len(text) > 5000:
             raise HTTPException(status_code=400, detail="Text inputs must be under 5000 characters")

        # Delegate purely to Gemini
        return await GeminiClient.analyze_text(text)

    @staticmethod
    def create_analysis(db: Session, analysis: AnalysisCreate, user_id: int) -> Analysis:
        new_analysis = Analysis(
            user_id=user_id,
            original_text=analysis.original_text,
            result=analysis.result
        )
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        return new_analysis

    @staticmethod
    def get_user_history(db: Session, user_id: int) -> List[Analysis]:
        return db.query(Analysis).filter(Analysis.user_id == user_id).order_by(Analysis.created_at.desc()).all()

    @staticmethod
    def get_analysis_by_id(db: Session, analysis_id: int, user_id: int) -> Analysis:
        return db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == user_id).first()
