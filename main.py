from fastapi import FastAPI
import models
from database import engine

app = FastAPI()

# Create all db tables and columns
models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def create_database():
    return {"Database": "Created"}
