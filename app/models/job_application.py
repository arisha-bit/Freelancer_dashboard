from sqlalchemy import Column, Integer, ForeignKey, Text, String
from sqlalchemy.orm import relationship
from app.database import Base

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    freelancer_id = Column(Integer, ForeignKey("users.id"))
    experience = Column(Text, nullable=False)
    resume_link = Column(String, nullable=False)
    cover_letter = Column(Text, nullable=False)
    status = Column(String, default="Pending")

    job = relationship("Job", back_populates="applications")
    freelancer = relationship("User", back_populates="applications")
