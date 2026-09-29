from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models  # noqa: F401 (ensures models are registered before create_all)
from .routers import auth, drives, applications

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Placement Management System API")

# Wide-open CORS for the college-project scale of this app.
# Tighten to your actual frontend URL before/at deployment if you want.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pms-frontend.vercel.app/login?returnUrl=%2Fdashboard"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(drives.router)
app.include_router(applications.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Smart Placement Management System API is running"}
