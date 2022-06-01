from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


# Create a new hashing context using bcrypt
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create DB and handle all setup if auth.py is ran before main.py
models.Base.metadata.create_all(bind=engine)

# Access token header information
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def get_db():
    """Create a local database session to pass into API routes

    Yields:
        db: A database session
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    """Generate a hash for a password

    Args:
        password (string): The password to hash

    Returns:
        string: A hash for a password
    """
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    """Compare plain text password with hashed password from database to verify the password is correct

    Args:
        plain_password (string): Plain text password to verify
        hashed_password (string): Hashed password to verify against
    """
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    """Authenticate a user

    Args:
        username (string): The username to authenticate
        password (string): The password to authenticate
        db (db): The database to search
    """
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, expires_delta: Optional[timedelta] = None
):
    """Create an access token

    Args:
        username (str): The username to create a token for
        user_id (int): The user_id to create a token for
        expires_delta (Optional[timedelta], optional): Expiration time for access token. Defaults to None.

    """
    # Create the user payload
    encode = {"sub": username, "id": user_id}

    if expires_delta:
        # Check that delta has not already expired
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    # Update user payload with expire time
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    """_summary_

    Args:
        token (str, optional): The token of the user to return. Defaults to Depends(oauth2_bearer).

    Raises:
        HTTPException: 404 - User not found
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="User not found")


# Create a new user
@app.post("/create/user")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):

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

    db.add(create_user_model)
    db.commit()


# Authorize a user
@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # TODO: Make this .env variable
    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    return {"token": token}


# Exceptions
def get_user_exception():
    """Create a custom exception response for decoding user info from JWT"""
    credentials_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception_response


def token_exception():
    """Create a custom exception response for authorizing user"""
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response
