from fastapi import FastAPI
import models
from database import engine, SessionLocal

app = FastAPI()

# Create all db tables and columns
models.Base.metadata.create_all(bind=engine)


# Create a local database session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
