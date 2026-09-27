from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/drives", tags=["drives"])


@router.post("", response_model=schemas.DriveOut)
def create_drive(
    payload: schemas.DriveIn,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    drive = models.Drive(
        company_name=payload.company_name,
        role_title=payload.role_title,
        jd_text=payload.jd_text,
        min_cgpa=payload.min_cgpa or 0.0,
        created_by=admin.id,
    )
    db.add(drive)
    db.commit()
    db.refresh(drive)
    return drive


@router.get("", response_model=List[schemas.DriveOut])
def list_drives(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    query = db.query(models.Drive)
    if current_user.role == "student":
        query = query.filter(models.Drive.min_cgpa <= current_user.cgpa)
    return query.order_by(models.Drive.created_at.desc()).all()
