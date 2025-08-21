from sqlalchemy.orm import Session
from app.models.job_application import JobApplication
from app.schemas.job_application import JobApplicationCreate

def apply_to_job(db: Session, application: JobApplicationCreate):
    new_app = JobApplication(
        job_id=application.job_id,
        freelancer_id=application.freelancer_id,
        experience=application.experience,
        resume_link=application.resume_link,
        cover_letter=application.cover_letter,
        status="Pending"
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

def get_applications_by_freelancer(db: Session, freelancer_id: int):
    return db.query(JobApplication).filter(JobApplication.freelancer_id == freelancer_id).all()

def get_applications_by_employer(db: Session, employer_id: int):
    return (
        db.query(JobApplication)
        .join(JobApplication.job)
        .filter(JobApplication.job.has(employer_id=employer_id))
        .all()
    )

def delete_application(db: Session, application_id: int):
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if app:
        db.delete(app)
        db.commit()
        return True
    return False

def update_application_status(db: Session, application_id: int, status: str):
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if app:
        app.status = status
        db.commit()
        return app
    return None
