from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from groq import RateLimitError
import re
from app.schemas.agent import *
from app.ai.format_agent import format_graph

router = APIRouter(
    prefix="/agent",
    tags=["agent"]
)

# --- STANDALONE HANDLER FUNCTION (No Decorator) ---
async def groq_rate_limit_handler(request: Request, exc: Exception):
    """
    Handler logic for Groq Rate Limits.
    """
    error_message = str(exc)
    
    # Regex parsing logic
    retry_match = re.search(r"Please try again in ([\w\.]+)", error_message)
    retry_after = retry_match.group(1) if retry_match else "a while"

    print(f"⚠️ GROQ RATE LIMIT HIT: {error_message}")

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "RATE_LIMIT_EXCEEDED",
            "message": "AI Processing limit reached. Please wait before retrying.",
            "detail": {
                "retry_after": retry_after,
                "provider": "Groq",
            }
        }
    )

@router.post("/format_agent", response_model=FormatAgentResponse)
async def format_agent_graph(data: FormatAgentBase):
    # Your existing endpoint logic
    raw_text = data.raw_text
    user_request = data.user_request
    result = await format_graph(raw_text=raw_text, user_query=user_request)
    return result