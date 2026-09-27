import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import requests

from .. import models, schemas, auth
from ..database import get_db
from ..ml.resume_matcher import compute_match_score
from ..ml.readiness_predictor import predict_readiness

router = APIRouter(prefix="/applications", tags=["applications"])

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")  # optional; set once you build the n8n workflow


def _notify(event: str, payload: dict):
    """Fire-and-forget webhook call to n8n. Safe no-op if not configured."""
    if not N8N_WEBHOOK_URL:
        return
    try:
        requests.post(N8N_WEBHOOK_URL, json={"event": event, **payload}, timeout=3)
    except requests.RequestException:
        pass  # never let a notification failure break the actual request


@router.post("/{drive_id}", response_model=schemas.ApplicationOut)
def apply_to_drive(
    drive_id: int,
    db: Session = Depends(get_db),
    student: models.User = Depends(auth.get_current_user),
):
    if student.role != "student":
        raise HTTPException(status_code=403, detail="Only students can apply")

    drive = db.query(models.Drive).filter(models.Drive.id == drive_id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    existing = (
        db.query(models.Application)
        .filter(models.Application.student_id == student.id, models.Application.drive_id == drive_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this drive")

    match_score = compute_match_score(student.resume_text, drive.jd_text)
    skill_count = len([s for s in (student.skills or "").split(",") if s.strip()])
    readiness_score = predict_readiness(
        cgpa=student.cgpa,
        backlogs=student.backlogs,
        internships=student.internships,
        certifications=student.certifications,
        skill_count=skill_count,
    )

    application = models.Application(
        student_id=student.id,
        drive_id=drive_id,
        match_score=match_score,
        readiness_score=readiness_score,
        status="applied",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    _notify("application_created", {
        "student_name": student.name,
        "student_email": student.email,
        "company_name": drive.company_name,
        "role_title": drive.role_title,
        "match_score": match_score,
        "readiness_score": readiness_score,
    })

    return application


@router.get("/me", response_model=List[schemas.ApplicationOut])
def my_applications(db: Session = Depends(get_db), student: models.User = Depends(auth.get_current_user)):
    return db.query(models.Application).filter(models.Application.student_id == student.id).all()


@router.get("/drive/{drive_id}", response_model=List[schemas.ApplicationOut])
def drive_applications(
    drive_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    return (
        db.query(models.Application)
        .filter(models.Application.drive_id == drive_id)
        .order_by(models.Application.match_score.desc())
        .all()
    )


@router.patch("/{application_id}/status", response_model=schemas.ApplicationOut)
def update_status(
    application_id: int,
    payload: schemas.StatusUpdateIn,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = payload.status
    db.commit()
    db.refresh(application)

    student = db.query(models.User).filter(models.User.id == application.student_id).first()
    drive = db.query(models.Drive).filter(models.Drive.id == application.drive_id).first()
    _notify("status_updated", {
        "student_name": student.name if student else "",
        "student_email": student.email if student else "",
        "company_name": drive.company_name if drive else "",
        "new_status": payload.status,
    })

    return application
