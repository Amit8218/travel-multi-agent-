import os
import logging
import time
import contextvars
from typing import Optional, Dict, Any

try:
    from langfuse import get_client
except ImportError:
    get_client = None

from app.config import (
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_HOST,
    LANGFUSE_ENABLED
)

logger = logging.getLogger("AI-Travel-Guide-Tracing")
logging.basicConfig(level=logging.INFO)

# Context variables for tracing state (holds (ctx, span) tuples)
active_trace_var = contextvars.ContextVar("active_trace", default=None)
active_span_var = contextvars.ContextVar("active_span", default=None)
supervisor_span_var = contextvars.ContextVar("supervisor_span", default=None)

_langfuse_client = None

def initialize_langfuse() -> Optional[Any]:
    """
    Initializes the Langfuse client if enabled and keys are present.
    """
    global _langfuse_client
    if not LANGFUSE_ENABLED:
        logger.info("Langfuse tracing is disabled.")
        return None

    if get_client is None:
        logger.warning("Langfuse package is not installed. Tracing is disabled.")
        return None

    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        logger.warning("Langfuse credentials not configured. Tracing is disabled.")
        return None

    try:
        _langfuse_client = get_client()
        logger.info("Langfuse OTel tracing client initialized successfully.")
        return _langfuse_client
    except Exception as e:
        logger.error(f"Failed to initialize Langfuse client: {e}")
        return None

def get_langfuse_client() -> Optional[Any]:
    """
    Returns the initialized Langfuse client or None.
    """
    global _langfuse_client
    if _langfuse_client is None:
        initialize_langfuse()
    return _langfuse_client

def is_tracing_enabled() -> bool:
    """
    Returns True if Langfuse tracing is active and client is ready.
    """
    try:
        return LANGFUSE_ENABLED and get_langfuse_client() is not None
    except Exception:
        return False

def create_trace(name: str, input: Optional[Any] = None, metadata: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """
    Creates a new root trace span and sets it in context.
    Returns the span object.
    """
    if not is_tracing_enabled():
        return None
    try:
        client = get_langfuse_client()
        ctx = client.start_as_current_observation(
            name=name,
            input=input,
            metadata=metadata
        )
        span = ctx.__enter__()
        active_trace_var.set((ctx, span))
        active_span_var.set(None)
        supervisor_span_var.set(None)
        logger.info(f"Langfuse trace '{name}' created with OTel Trace ID: {span.trace_id}")
        return span
    except Exception as e:
        logger.warning(f"Error creating trace: {e}")
        return None

def create_span(name: str, input: Optional[Any] = None, metadata: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """
    Creates a child span under the current active OTel context.
    Returns a tuple (ctx, span).
    """
    if not is_tracing_enabled():
        return None
    try:
        client = get_langfuse_client()
        ctx = client.start_as_current_observation(
            name=name,
            input=input,
            metadata=metadata
        )
        span = ctx.__enter__()
        
        span_data = (ctx, span)
        active_span_var.set(span_data)
        if name == "supervisor_agent":
            supervisor_span_var.set(span_data)
            
        return span_data
    except Exception as e:
        logger.warning(f"Error creating span: {e}")
        return None

def end_span(span_data: Optional[Any], output: Optional[Any] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Ends a span context manager, updating output/metadata if provided.
    """
    if not is_tracing_enabled() or span_data is None:
        return
    try:
        if isinstance(span_data, tuple) and len(span_data) == 2:
            ctx, span = span_data
            if span and hasattr(span, "update"):
                span.update(output=output, metadata=metadata)
            ctx.__exit__(None, None, None)
        elif hasattr(span_data, "end"):
            span_data.end(output=output, metadata=metadata)
        elif hasattr(span_data, "update"):
            span_data.update(output=output, metadata=metadata)
    except Exception as e:
        logger.warning(f"Error ending span: {e}")

def trace_agent_step(agent_name: str, input_data: Any, output_data: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    A helper function to log a complete agent step.
    """
    if not is_tracing_enabled():
        return
    try:
        span_data = create_span(name=agent_name, input=input_data, metadata=metadata)
        if span_data:
            end_span(span_data, output=output_data)
    except Exception as e:
        logger.warning(f"Error tracing agent step: {e}")

def trace_tool_call(tool_name: str, input_data: Any, output_data: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    A helper function to log a tool call span.
    """
    if not is_tracing_enabled():
        return
    try:
        span_data = create_span(name=tool_name, input=input_data, metadata=metadata)
        if span_data:
            end_span(span_data, output=output_data)
    except Exception as e:
        logger.warning(f"Error tracing tool call: {e}")

def trace_error(error_msg: str, details: Optional[Any] = None) -> None:
    """
    Logs an error to the active span.
    """
    if not is_tracing_enabled():
        return
    try:
        active_data = active_span_var.get() or active_trace_var.get()
        if active_data:
            span = active_data[1] if isinstance(active_data, tuple) else active_data
            if span and hasattr(span, "update"):
                span.update(
                    level="ERROR",
                    status_message=error_msg,
                    metadata={"error_details": str(details)} if details else None
                )
    except Exception as e:
        logger.warning(f"Error logging trace error: {e}")

def flush_traces() -> None:
    """
    Forces sending trace details to Langfuse servers.
    """
    if not is_tracing_enabled():
        return
    try:
        client = get_langfuse_client()
        client.flush()
    except Exception as e:
        logger.warning(f"Error flushing traces: {e}")

def copy_context_to_thread(func, *args, **kwargs):
    """
    Helper to execute func with the current contextvars copied.
    Crucial for propagating active spans/traces to thread pool threads.
    """
    ctx = contextvars.copy_context()
    return ctx.run(func, *args, **kwargs)
