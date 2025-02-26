from sqlalchemy import Column, BigInteger, Text, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class EmploymentMinstat(Base):
    __tablename__ = "employment_minstat"

    id = Column(BigInteger, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    number_of_employees = Column(Float, nullable=False)
    salary = Column(Float, nullable=False)
    
    # Foreign key that references the OKVED section.
    okved_section_id = Column(BigInteger, ForeignKey("okved_sections.id"), nullable=False)
    
    # Relationship back to the OkvedSection.
    okved_section = relationship("OkvedSection", back_populates="employments")