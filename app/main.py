# main.py

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app import models
from app.database import SessionLocal, engine
from app.models.user import User
from app.models.job import Job
from app.models.job_application import JobApplication
from app.schemas.job import JobCreate
from app.schemas.job_application import JobApplicationCreate
from app.crud import user as user_crud
from app.crud import job as job_crud
from app.crud import job_application as app_crud

# ------------------ App Setup ------------------
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# ------------------ DB Dependency ------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ Home & Auth ------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = user_crud.get_user_by_email(db, email=email)
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered"}
        )
    user_crud.create_user(db=db, name=name, email=email, password=password, role=role)
    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_user(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    user_obj = user_crud.get_user_by_email(db, email=email)
    if user_obj is None or getattr(user_obj, "password", None) != password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"}
        )
    if getattr(user_obj, "role", None) == "freelancer":
        return RedirectResponse(f"/freelancer/dashboard?user_id={user_obj.id}", status_code=303)
    else:
        return RedirectResponse(f"/employer/dashboard?user_id={user_obj.id}", status_code=303)

@app.get("/logout")
def logout():
    return RedirectResponse("/", status_code=303)

# ------------------ Freelancer Routes ------------------
@app.get("/freelancer/dashboard", response_class=HTMLResponse)
def freelancer_dashboard(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    success: Optional[str] = None
):
    jobs = job_crud.get_all_jobs(db)
    applications = app_crud.get_applications_by_freelancer(db, freelancer_id=user_id)
    return templates.TemplateResponse(
        "freelancer/dashboard.html",
        {
            "request": request,
            "jobs": jobs,
            "applications": applications,
            "freelancer_id": user_id,
            "success": success
        }
    )

@app.get("/freelancer/apply/{job_id}", response_class=HTMLResponse)
def application_form(request: Request, job_id: int, freelancer_id: int):
    return templates.TemplateResponse(
        "freelancer/apply_form.html",
        {"request": request, "job_id": job_id, "freelancer_id": freelancer_id}
    )

@app.post("/freelancer/apply/{job_id}")
def apply_to_job(
    job_id: int,
    freelancer_id: int = Form(...),
    experience: str = Form(...),
    resume_link: str = Form(...),
    cover_letter: str = Form(...),
    db: Session = Depends(get_db)
):
    app_data = JobApplicationCreate(
        job_id=job_id,
        freelancer_id=freelancer_id,
        experience=experience,
        resume_link=resume_link,
        cover_letter=cover_letter
    )
    app_crud.apply_to_job(db, app_data)
    return RedirectResponse(
        f"/freelancer/dashboard?user_id={freelancer_id}&success=Application+submitted!",
        status_code=303
    )

@app.post("/freelancer/delete-application/{application_id}")
def delete_application(application_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    app_crud.delete_application(db, application_id)
    return RedirectResponse(
        f"/freelancer/dashboard?user_id={user_id}&success=Application+deleted!",
        status_code=303
    )
    from app.models.job_application import JobApplication  # make sure this import exists

# Freelancer Available Jobs Page
@app.get("/freelancer/{freelancer_id}/jobs", response_class=HTMLResponse)
def freelancer_jobs(request: Request, freelancer_id: int, db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return templates.TemplateResponse("freelancer/freelancer_jobs.html", {
        "request": request,
        "jobs": jobs,
        "freelancer_id": freelancer_id
    })

# Freelancer Applied Jobs Page
@app.get("/freelancer/{freelancer_id}/applications", response_class=HTMLResponse)
def freelancer_applications(request: Request, freelancer_id: int, db: Session = Depends(get_db)):
    applications = db.query(JobApplication).filter(JobApplication.freelancer_id == freelancer_id).all()
    return templates.TemplateResponse("freelancer/freelancer_applications.html", {
        "request": request,
        "applications": applications,
        "freelancer_id": freelancer_id
    })


# ------------------ Employer Routes ------------------
@app.get("/employer/dashboard", response_class=HTMLResponse)
def employer_dashboard(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    success: Optional[str] = None
):
    jobs = job_crud.get_jobs_by_employer(db, employer_id=user_id)
    applications = app_crud.get_applications_by_employer(db, employer_id=user_id)
    return templates.TemplateResponse(
        "employer/dashboard.html",
        {
            "request": request,
            "jobs": jobs,
            "applications": applications,
            "user_id": user_id,
            "success": success
        }
    )

@app.get("/employer/jobs", response_class=HTMLResponse)
def employer_jobs(request: Request, user_id: int, db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.employer_id == user_id).all()
    return templates.TemplateResponse("employer/employer_jobs.html", {
        "request": request,
        "user_id": user_id,
        "jobs": jobs
    })

@app.post("/employer/delete-job/{job_id}")
def delete_job(job_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        db.delete(job)
        db.commit()
    return RedirectResponse(url=f"/employer/jobs?user_id={user_id}&success=Job+deleted!", status_code=303)

@app.get("/employer/applications", response_class=HTMLResponse)
def employer_applications(request: Request, user_id: int, db: Session = Depends(get_db)):
    applications = (
        db.query(JobApplication)
        .join(Job, Job.id == JobApplication.job_id)
        .filter(Job.employer_id == user_id)
        .all()
    )
    return templates.TemplateResponse("employer/employer_applications.html", {
        "request": request,
        "user_id": user_id,
        "applications": applications
    })

@app.post("/employer/decision/{application_id}")
def employer_decision(
    application_id: int, 
    user_id: int = Form(...), 
    status: str = Form(...), 
    db: Session = Depends(get_db)
):
    db.query(JobApplication).filter(JobApplication.id == application_id).update(
        {"status": status}
    )
    db.commit()
    return RedirectResponse(
        url=f"/employer/applications?user_id={user_id}&success=Status+updated!", 
        status_code=303
    )

@app.get("/employer/post-job", response_class=HTMLResponse)
def post_job_form(request: Request, user_id: int):
    return templates.TemplateResponse("employer/post_job.html", {"request": request, "user_id": user_id})

@app.post("/employer/post-job")
def post_job(
    title: str = Form(...),
    description: str = Form(...),
    employer_id: int = Form(...),
    db: Session = Depends(get_db)
):
    job_data = JobCreate(title=title, description=description)
    job_crud.create_job(db=db, job=job_data, employer_id=employer_id)
    return RedirectResponse(
        f"/employer/dashboard?user_id={employer_id}&success=Job+posted+successfully!",
        status_code=303
    )
