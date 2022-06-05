from fastapi import HTTPException, status

def http_exception():
    """Generate a general HTTP exception for a task with a 404 status code"""
    return HTTPException(status_code=404, detail="Task not found")

def get_user_exception():
    """Create a custom exception response for decoding user info from JWT"""
    credentials_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception_response

def bad_request_exception():
    return HTTPException(status_code=400, detail="Bad request please check your request and try again")

def forbidden_request_exception():
    return HTTPException(status_code=403, detail="Request is forbidden")