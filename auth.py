from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


# Create a new hashing context using bcrypt
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()


def get_password_hash(password):
    """Generate a hash for a password

    Args:
        password (string): The password to hash

    Returns:
        string: A hash for a password
    """
    return bcrypt_context.hash(password)


# Create a new user
@app.post("/create/user")
async def create_new_user(create_user: CreateUser):

    # Map the task to the DB model
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name

    hashed_password = get_password_hash(create_user.password)

    create_user_model.hashed_password = hashed_password
    create_user_model.last_name = create_user.last_name
    create_user_model.is_active = True

    return create_user_model
