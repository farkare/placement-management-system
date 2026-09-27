from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"  # "student" or "admin"
    cgpa: Optional[float] = 0.0
    backlogs: Optional[int] = 0
    internships: Optional[int] = 0
    certifications: Optional[int] = 0
    skills: Optional[str] = ""
    resume_text: Optional[str] = ""


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    cgpa: float
    backlogs: int
    internships: int
    certifications: int
    skills: str
    resume_text: str

    class Config:
        from_attributes = True


class DriveIn(BaseModel):
    company_name: str
    role_title: str
    jd_text: str
    min_cgpa: Optional[float] = 0.0


class DriveOut(BaseModel):
    id: int
    company_name: str
    role_title: str
    jd_text: str
    min_cgpa: float

    class Config:
        from_attributes = True


class ApplicationOut(BaseModel):
    id: int
    student_id: int
    drive_id: int
    match_score: float
    readiness_score: float
    status: str

    class Config:
        from_attributes = True


class StatusUpdateIn(BaseModel):
    status: str  # applied / shortlisted / rejected / selected
