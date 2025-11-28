import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Get the connection string from environment variables
# Set this in your environment: export DATABASE_URL="postgresql://user:password@host:port/dbname"
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/sme_copilot_db")

# Create the engine (the actual connection handler)
engine = create_engine(
    DATABASE_URL
)

# Create a configured "Session" class
# This will be the handler you use to talk to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for your models (ORM definitions)
Base = declarative_base()

def get_db():
    """Dependency to get a new DB session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()