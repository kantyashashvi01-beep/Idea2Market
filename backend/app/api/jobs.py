from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Job, User
from app.schemas.api_schemas import JobOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=JobOut)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Job not found."}},
        )

    # Ownership check: verify project belongs to user
    if job.project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "forbidden", "message": "Access denied to this job."}},
        )

    # Check for stale running job (e.g. Render restart)
    if job.status == "running" and job.created_at:
        now = datetime.now(timezone.utc)
        if now - job.created_at > timedelta(minutes=10):
            job.status = "failed"
            job.error_message = "Generation timed out or worker restarted."
            db.commit()

    return JobOut(
        id=job.id,
        project_id=job.project_id,
        status=job.status,
        stage=job.stage,
        progress_percent=job.progress_percent,
        error_message=job.error_message,
    )
