import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace 'your_password' with the password you set for PostgreSQL
# DATABASE_URL = "postgresql://postgres:avishek.123@localhost/civic_sathi_db"
# This will get the database URL from Render's environment variables.
# If it can't find it, it will fall back to your local setup.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:your_password@localhost/civic_sathi_db")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This is a helper function to get a database session when we need one.
# We are preparing it now for Phase 3.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()