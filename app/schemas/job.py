# app/schemas/job.py
from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    description: str

class JobOut(JobCreate):
    id: int
    employer_id: int

    class Config:
        from_attributes = True  # Updated for Pydantic v2
