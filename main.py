from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field


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


class Task(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="The priority must be between 1-5")
    complete: bool


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
    raise http_exception()


# Add a new task
@app.post("/")
async def create_task(task: Task, db: Session = Depends(get_db)):
    # Map the task to the DB model
    task_model = models.Tasks()
    task_model.title = task.title
    task_model.description = task.description
    task_model.priority = task.priority
    task_model.complete = task.complete

    # Add to DB and commit
    db.add(task_model)
    db.commit()

    return successful_response(201)


# Update an existing task by ID
@app.put("/{task_id}")
async def update_task(task_id: int, task: Task, db: Session = Depends(get_db)):
    task_model = db.query(models.Tasks).filter(models.Tasks.id == task_id).first()

    if task_model is None:
        raise http_exception()

    # Map the task to the DB model
    task_model.title = task.title
    task_model.description = task.description
    task_model.priority = task.priority
    task_model.complete = task.complete

    # Add to DB and commit
    db.add(task_model)
    db.commit()

    return successful_response(200)


# Remove an existing task by ID
@app.put("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_model = db.query(models.Tasks).filter(models.Tasks.id == task_id).first()

    if task_model is None:
        raise http_exception()

    db.query(models.Tasks).filter(models.Tasks.id == task_id).delete()

    db.commit()

    return successful_response(201)


# Generate a success response
def successful_response(status_code: int):
    return {"status": status_code, "transaction": "Successful"}


# General exception users for tasks
def http_exception():
    return HTTPException(status_code=404, detail="Task not found")
