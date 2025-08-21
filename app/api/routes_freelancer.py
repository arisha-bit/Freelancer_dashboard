# app/api/routes_freelancer.py

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from typing import Optional  # <-- Added

from app.database import SessionLocal
from app.crud import job

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard")
def freelancer_dashboard(
    request: Request,
    user_id: int,  # query parameter
    db: Session = Depends(get_db),
    success: Optional[str] = None
):
    jobs = job.get_all_jobs(db)
    return templates.TemplateResponse(
        "freelancer/dashboard.html",
        {
            "request": request,
            "jobs": jobs,
            "freelancer_id": user_id,
            "success": success
        }
    )
