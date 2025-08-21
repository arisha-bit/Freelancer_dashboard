from pydantic import BaseModel

class JobApplicationCreate(BaseModel):
    job_id: int
    freelancer_id: int
    experience: str
    resume_link: str
    cover_letter: str
