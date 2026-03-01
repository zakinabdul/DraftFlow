from fastapi import FastAPI
from app.api.v2 import api_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.v2.agents import groq_rate_limit_handler
from groq import RateLimitError
from contextlib import asynccontextmanager


app = FastAPI()
@app.get("/")
def index_mesg():
    return {
        "message": "Use /docs endpoint for now"
    }
    
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix="/api/v2")
app.add_exception_handler(RateLimitError, groq_rate_limit_handler)
