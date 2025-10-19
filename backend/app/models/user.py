import uuid
from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    
    user_uid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)

    name = Column(Text, nullable=False)
    child_name = Column(Text, nullable=False)
    group_name = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    
    booking = relationship("Booking", uselist=False, back_populates="user")