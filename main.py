from statistics import mode
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from auth import get_current_user
from exceptions import get_user_exception, http_exception

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


# Read all tasks by current logged in user
@app.get("/tasks/user")
async def read_all_by_user(
    user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    print(user)
    return db.query(models.Tasks).filter(models.Tasks.owner_id == user.get("id")).all()


# Read task based on ID
@app.get("/task/{task_id}")
async def read_task(
    task_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    task_model = (
        db.query(models.Tasks)
        .filter(models.Tasks.id == task_id)
        .filter(models.Tasks.owner_id == user.get("id"))
        .first()
    )

    if task_model is not None:
        return task_model
    raise http_exception()


# Add a new task
@app.post("/")
async def create_task(
    task: Task, user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    # Map the task to the DB model
    task_model = models.Tasks()
    task_model.title = task.title
    task_model.description = task.description
    task_model.priority = task.priority
    task_model.complete = task.complete
    task_model.owner_id = user.get("id")

    # Add to DB and commit
    db.add(task_model)
    db.commit()

    return successful_response(201)


# Update an existing task by ID
# TODO: Test this in Postman
@app.put("/{task_id}")
async def update_task(
    task_id: int,
    task: Task,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    if user is None:
        raise get_user_exception()

    task_model = (
        db.query(models.Tasks)
        .filter(models.Tasks.id == task_id)
        .filter(models.Tasks.owner_id == user.get("id"))
        .first()
    )

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
# TODO: Test this in Postman
@app.delete("/{task_id}")
async def delete_task(
    task_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):

    if user is None:
        raise get_user_exception()

    task_model = (
        db.query(models.Tasks)
        .filter(models.Tasks.id == task_id)
        .filter(models.Tasks.owner_id == user.get("id"))
        .first()
    )

    if task_model is None:
        raise http_exception()

    db.delete(task_model)

    db.commit()

    return successful_response(201)


def successful_response(status_code: int):
    """Generate a successful response including a status code and message

    Args:
        status_code (int): The status code to return

    """
    return {"status": status_code, "transaction": "Successful"}
