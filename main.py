from fastapi import FastAPI, Depends
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

# Create all db tables and columns
models.Base.metadata.create_all(bind=engine)


# Create a local database session to pass into API routes
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Read all tasks
@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Tasks).all()
