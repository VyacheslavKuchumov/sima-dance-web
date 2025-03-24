async def process_message(message: str) -> str:
    """
    Process the incoming WebSocket message.
    Currently, this function simply echoes back the message with a prefix.
    """
    print(f"Received message: {message}")
    # Add any additional business logic here
    return f"{message}"
