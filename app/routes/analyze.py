from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analysis import AnalysisRequest, AnalysisCreate
from app.schemas.ai_analysis import AIAnalysisResponse
from app.services.analysis_service import AnalysisService
from app.models.user import User
from app.utils.rate_limiter import rate_limit_dependency
from typing import Optional
from app.config import settings
from jose import JWTError, jwt

router = APIRouter()

async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    return db.query(User).filter(User.id == int(user_id)).first()


@router.post("/", response_model=AIAnalysisResponse)
async def analyze_text(
    request: Request,
    body: AnalysisRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    # Check rate limit if anonymous
    if not current_user:
        await rate_limit_dependency(request)

    if not body.text or not body.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    if len(body.text) > 5000:
        raise HTTPException(status_code=400, detail="Input text exceeds 5000 characters")

    # Perform Fully AI Analysis (Async)
    # returns AIAnalysisResponse object
    ai_result = await AnalysisService.perform_ai_analysis(body.text)
    
    # Save if authenticated
    if current_user:
        analysis_create = AnalysisCreate(
            original_text=body.text,
            result=ai_result.model_dump()
        )
        AnalysisService.create_analysis(db, analysis_create, current_user.id)
    
    # Always return the AI structure directly
    return ai_result
