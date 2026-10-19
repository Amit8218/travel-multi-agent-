import os
import logging
from contextlib import contextmanager
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

logger = logging.getLogger("AI-Travel-Guide-Agent")

class BaseAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        
        # Initialize ChatOpenAI pointing to OpenRouter
        # Provide fallback if api_key is missing or empty
        api_key = OPENROUTER_API_KEY if OPENROUTER_API_KEY else "dummy_key"
        
        self.llm = ChatOpenAI(
            model=OPENROUTER_MODEL,
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            temperature=0.2,
            timeout=60,
        )

    @contextmanager
    def trace_agent(self, input_data: dict, user_query: str = ""):
        """
        Context manager to automatically trace agent execution, inputs, outputs, status, and exceptions.
        """
        from app.tracing import create_span, end_span, active_span_var
        
        logger.info(f"Agent '{self.name}' started execution.")
        span_data = None
        token = None
        span_name = f"{self.name}_agent"
        
        # Initial metadata
        metadata = {
            "agent_name": self.name,
            "user_query": user_query,
            "model": OPENROUTER_MODEL,
            "status": "success"
        }
        
        try:
            span_data = create_span(
                name=span_name,
                input=input_data,
                metadata=metadata
            )
            # span_data is (ctx, span)
            span_obj = span_data[1] if span_data else None
            
            if span_data:
                token = active_span_var.set(span_data)
                
            class AgentTraceContext:
                def __init__(self, span_val, meta):
                    self.span = span_val
                    self.metadata = meta
                    self.output = None
                    self.status = "success"

                def set_output(self, output: Any):
                    self.output = output
                    if self.span:
                        try:
                            self.span.update(output=output)
                        except Exception as e:
                            logger.warning(f"Error updating span output for agent {self.name}: {e}")

                def set_error(self, error_msg: str):
                    self.status = "error"
                    self.metadata["status"] = "error"
                    if self.span:
                        try:
                            self.span.update(
                                level="ERROR",
                                status_message=error_msg,
                                metadata={**self.metadata, "error": error_msg}
                            )
                        except Exception as e:
                            logger.warning(f"Error updating span error status for agent {self.name}: {e}")
            
            # Use forward reference wrapper for type annotation if needed, but local is fine
            import typing
            from typing import Any
            ctx = AgentTraceContext(span_obj, metadata)
            yield ctx
            
            # Post-execution metadata sync
            if span_obj:
                try:
                    span_obj.update(metadata={**metadata, "status": ctx.status})
                except Exception as e:
                    logger.warning(f"Error updating post-run span metadata for agent {self.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Exception during agent '{self.name}' run: {e}")
            if span_obj:
                try:
                    span_obj.update(
                        level="ERROR",
                        status_message=str(e),
                        metadata={**metadata, "status": "error", "error": str(e)}
                    )
                except Exception as ex:
                    logger.warning(f"Error updating span exception for agent {self.name}: {ex}")
            raise e
        finally:
            if span_data:
                end_span(span_data)
            if token is not None:
                active_span_var.reset(token)
            logger.info(f"Agent '{self.name}' completed execution.")


    def generate_response(self, user_query: str, chat_history: list = None) -> str:
        """
        Executes a prompt against the configured OpenRouter LLM.
        Gracefully handles API keys and rate limiting/failures.
        """
        if not OPENROUTER_API_KEY:
            return (
                "Configuration Error: OPENROUTER_API_KEY is not set.\n"
                "Please configure OPENROUTER_API_KEY in your environment or .env file."
            )
            
        messages = [SystemMessage(content=self.system_prompt)]
        if chat_history:
            messages.extend(chat_history)
        messages.append(HumanMessage(content=user_query))
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            error_str = str(e).lower()
            # Handle rate limit or model availability errors
            if "rate limit" in error_str or "429" in error_str or "unavailable" in error_str or "503" in error_str:
                return (
                    "The free OpenRouter model may be rate-limited or unavailable. "
                    "Try again later or set another model in OPENROUTER_MODEL."
                )
            return f"Error executing agent '{self.name}': {str(e)}"
