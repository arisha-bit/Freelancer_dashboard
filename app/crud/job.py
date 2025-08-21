from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate

def create_job(db: Session, job: JobCreate, employer_id: int):
    db_job = Job(**job.dict(), employer_id=employer_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_all_jobs(db: Session):
    return db.query(Job).all()

def get_jobs_by_employer(db: Session, employer_id: int):
    return db.query(Job).filter(Job.employer_id == employer_id).all()

def get_job_by_id(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()

def delete_job(db: Session, job_id: int):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job:
        db.delete(db_job)
        db.commit()
        return True
    return False
