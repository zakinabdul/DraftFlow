from fastapi import APIRouter
from app.schemas.agent import *
from app.ai.format_agent import format_graph
import asyncio
router = APIRouter(
    prefix="/agent",
   tags=["agent"]
)

@router.post("/format_agent", response_model=FormatAgentResponse)
async def format_agent_graph(data: FormatAgentBase):
    raw_text = data.raw_text
    doc_type = data.doc_type
    result = await format_graph(raw_text=raw_text, doc_type=doc_type)
    
    return result
    
    
    
