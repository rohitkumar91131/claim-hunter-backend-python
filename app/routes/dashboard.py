from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.dashboard import DashboardStats, RiskDistribution, RecentAnalysis

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregated analysis statistics for the authenticated user."""
    analyses = (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .all()
    )

    risk_counts = {"Low": 0, "Medium": 0, "High": 0}
    scores = []

    for analysis in analyses:
        risk = analysis.result.get("overall_risk_level")
        if risk in risk_counts:
            risk_counts[risk] += 1
        score = analysis.result.get("summary_score")
        if score is not None:
            scores.append(score)

    average_score = round(sum(scores) / len(scores), 2) if scores else 0.0

    recent = (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(5)
        .all()
    )

    recent_analyses = [
        RecentAnalysis(
            id=a.id,
            original_text=(
                a.original_text[:100] + "..."
                if len(a.original_text) > 100
                else a.original_text
            ),
            summary_score=a.result.get("summary_score", 0),
            overall_risk_level=a.result.get("overall_risk_level", "Unknown"),
            created_at=a.created_at,
        )
        for a in recent
    ]

    return DashboardStats(
        total_analyses=len(analyses),
        risk_distribution=RiskDistribution(
            low=risk_counts["Low"],
            medium=risk_counts["Medium"],
            high=risk_counts["High"],
        ),
        recent_analyses=recent_analyses,
        average_score=average_score,
    )
