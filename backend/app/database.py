from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       pool_size=100,         # The number of connections to keep open inside the pool.
    max_overflow=50,     # The maximum number of connections that can be created beyond the pool_size.
    pool_timeout=30,     # The maximum number of seconds to wait for a connection.
    pool_recycle=1800,  # The number of seconds after which a connection is automatically recycled.
    pool_pre_ping=True)  # Check if the connection is still valid before using it.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
