def successful_response(status_code: int):
    """Generate a successful response including a status code and message

    Args:
        status_code (int): The status code to return

    """
    return {"status": status_code, "transaction": "Successful"}