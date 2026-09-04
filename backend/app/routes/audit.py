from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import AuditLog
from app.schemas import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit Trail & Explainability"])

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    goal_id: Optional[int] = None,
    limit: int = 250,
    db: Session = Depends(get_db)
):
    """
    Returns full transparent audit trail ordered chronologically (newest first).
    Each entry provides deep explainability for agent decisions, policy evaluations,
    human sign-offs, Razorpay test link creations, and payment outcomes.
    """
    query = db.query(AuditLog)
    if goal_id:
        query = query.filter(AuditLog.goal_id == goal_id)
    logs = query.order_by(AuditLog.id.desc()).limit(limit).all()
    return logs
