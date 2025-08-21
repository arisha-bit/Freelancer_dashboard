from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from app.database import SessionLocal
from app.crud import job
from app.crud import job_application
from app.schemas.job import JobCreate
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ Employer Dashboard ------------------
@router.get("/dashboard")
def employer_dashboard(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    success: Optional[str] = None
):
    applications = job_application.get_applications_by_employer(db, employer_id=user_id)
    jobs = job.get_jobs_by_employer(db, employer_id=user_id)

    return templates.TemplateResponse("employer/dashboard.html", {
        "request": request,
        "applications": applications,
        "jobs": jobs,
        "user_id": user_id,
        "success": success
    })

# ------------------ Post Job ------------------

@router.get("/post-job")
def post_job_form(request: Request, user_id: int):
    return templates.TemplateResponse("employer/post_job.html", {
        "request": request,
        "user_id": user_id
    })

@router.post("/post-job")
def post_job(
    title: str = Form(...),
    description: str = Form(...),
    employer_id: int = Form(...),  # ✅ Accept dynamically
    db: Session = Depends(get_db),
):
    job_data = JobCreate(title=title, description=description)
    job.create_job(db, job_data, employer_id)
    return RedirectResponse(
        f"/employer/dashboard?user_id={employer_id}&success=Job+posted+successfully!",
        status_code=303
    )
