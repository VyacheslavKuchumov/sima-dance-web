import asyncio
import json

# Global asynchronous queue for SSE messages
message_queue = asyncio.Queue()

async def event_stream():
    while True:
        # Wait until a new message is available
        data = await message_queue.get()
        # Yield the SSE formatted message
        yield f"data: {json.dumps(data)}\n\n"

def message(data):
    """
    Push a new message to the queue.
    This function can be called from synchronous code.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(message_queue.put(data))
    except RuntimeError:
        # No running event loop, create one
        asyncio.run(message_queue.put(data))
