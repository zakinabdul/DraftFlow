from fastapi import APIRouter
from app.api.v2.agents import router as agent_router

api_router = APIRouter()
api_router.include_router(agent_router)


