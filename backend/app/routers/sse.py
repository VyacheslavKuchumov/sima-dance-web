from fastapi import APIRouter

from app.controllers.sse import event_stream

from fastapi.responses import StreamingResponse



router = APIRouter()


# get updates
@router.get("/updates")
async def get_updates_route():
    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Helps disable buffering in some proxies
        })

