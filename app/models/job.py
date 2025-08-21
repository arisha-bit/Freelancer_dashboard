from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    employer_id = Column(Integer, ForeignKey("users.id"))

    # 🔗 Relationships
    employer = relationship("User", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job")
