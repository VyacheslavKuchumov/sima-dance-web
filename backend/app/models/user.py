import uuid
from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
     # Here we define user_uid as both the primary reference for the user and a foreign key
    # that points to Auth.auth_uid.
    user_uid = Column(UUID(as_uuid=True), ForeignKey("auths.auth_uid"), unique=True, index=True, default=uuid.uuid4)
    
    name = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Establishes the association to the Auth model
    auth = relationship("Auth", back_populates="user", uselist=False)