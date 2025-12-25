from fastapi import APIRouter
from app.schemas.agent import *
from app.ai.format_agent import format_graph
router = APIRouter(
    prefix="/agent",
   tags=["agent"]
)

# Format Agent Endpoint
@router.post("/format_agent", response_model=FormatAgentResponse)
async def format_agent_graph(data: FormatAgentBase):
    raw_text = data.raw_text
    user_request = data.user_request
    result = await format_graph(raw_text=raw_text, user_query=user_request)
    return result
    
    
    
