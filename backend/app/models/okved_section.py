from sqlalchemy import Column, BigInteger, Text, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class OkvedSection(Base):
    __tablename__ = "okved_sections"

    id = Column(BigInteger, primary_key=True, index=True)
    code = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    
    # One-to-many relationship: one OKVED section can have many employment records.
    employments = relationship(
        "EmploymentMinstat",
        back_populates="okved_section",
        # cascade="all, delete-orphan"
    )