from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import AnalysisService
from app.routes.auth import get_current_user
from app.models.user import User
from typing import List

router = APIRouter()

@router.get("/", response_model=List[AnalysisResponse])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return AnalysisService.get_user_history(db, current_user.id)

@router.get("/{id}", response_model=AnalysisResponse)
def get_analysis(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = AnalysisService.get_analysis_by_id(db, id, current_user.id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
