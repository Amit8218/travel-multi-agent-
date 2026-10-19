import json
import asyncio
from typing import Any, AsyncGenerator, Optional

def safe_json_dumps(data: Any) -> str:
    """
    Safely dumps a JSON object to string, returning '{}' on failure.
    """
    try:
        return json.dumps(data)
    except Exception:
        return "{}"

def format_sse(event: str, data: dict) -> str:
    """
    Formats data into a standard Server-Sent Event string.
    """
    return f"event: {event}\ndata: {safe_json_dumps(data)}\n\n"

async def stream_text_chunks(text: str, chunk_size: int = 20, delay: float = 0.01) -> AsyncGenerator[str, None]:
    """
    Asynchronously yields chunks of a string, introducing a delay to simulate natural streaming.
    """
    if not text:
        return
    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]
        await asyncio.sleep(delay)

async def stream_answer_only(final_answer: str) -> AsyncGenerator[str, None]:
    """
    Asynchronously yields formatted SSE token events for the final answer.
    """
    async for chunk in stream_text_chunks(final_answer):
        yield format_sse("token", {"content": chunk})


def stream_error(error_message: str) -> str:
    """
    Formats a standard SSE error event.
    """
    return format_sse("error", {"message": error_message})

def create_progress_event(agent_name: str, status: str, message: Optional[str] = None) -> str:
    """
    Formats a standard SSE progress event.
    """
    data = {"agent": agent_name, "status": status}
    if message:
        data["message"] = message
    return format_sse("progress", data)
