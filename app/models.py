from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")  # "student" or "admin"

    # student-only fields (blank for admins)
    cgpa = Column(Float, default=0.0)
    backlogs = Column(Integer, default=0)
    internships = Column(Integer, default=0)
    certifications = Column(Integer, default=0)
    skills = Column(Text, default="")        # comma separated
    resume_text = Column(Text, default="")   # pasted resume / skills+projects summary

    applications = relationship("Application", back_populates="student")


class Drive(Base):
    __tablename__ = "drives"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    role_title = Column(String, nullable=False)
    jd_text = Column(Text, nullable=False)
    min_cgpa = Column(Float, default=0.0)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applications = relationship("Application", back_populates="drive")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    drive_id = Column(Integer, ForeignKey("drives.id"))
    match_score = Column(Float, default=0.0)      # resume <-> JD similarity, 0-100
    readiness_score = Column(Float, default=0.0)  # ML placement-readiness probability, 0-100
    status = Column(String, default="applied")    # applied / shortlisted / rejected / selected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="applications")
    drive = relationship("Drive", back_populates="applications")
