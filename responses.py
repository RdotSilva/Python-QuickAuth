def successful_response(status_code: int):
    """Generate a successful response including a status code and message

    Args:
        status_code (int): The status code to return

    """
    return {"status": status_code, "transaction": "Successful"}


def successful_task_created_response():
    """Generate a successful response including a 201 status code and message when a task is successfully created"""
    return {"status": 201, "transaction": "Successfully created task"}


def successful_task_updated_response():
    """Generate a successful response including a 200 status code and message when a task is successfully updated"""
    return {"status": 200, "transaction": "Successfully updated task"}
