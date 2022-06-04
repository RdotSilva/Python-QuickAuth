from fastapi import  HTTPException

def http_exception():
    """Generate a general HTTP exception for a task with a 404 status code"""
    return HTTPException(status_code=404, detail="Task not found")