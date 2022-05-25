from fastapi import FastAPI, Depends, HTTPException
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


# Read task based on ID
@app.get("/task/{task_id}")
async def read_task(task_id: int, db: Session = Depends(get_db)):
    task_model = db.query(models.Tasks).filter(models.Tasks.id == task_id).first()

    if task_model is not None:
        return task_model
    raise HTTPException(status_code=404, detail="Task not found")
