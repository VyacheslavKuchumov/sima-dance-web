import uuid
from sqlalchemy import Column, BigInteger, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class Auth(Base):
    __tablename__ = "auths"

    id = Column(BigInteger, primary_key=True, index=True)
    auth_uid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    AccessToken = Column(Text, nullable=True)
    RefreshToken = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to User; one-to-one association (each auth record has one user)
    user = relationship("User", back_populates="auth", uselist=False)
