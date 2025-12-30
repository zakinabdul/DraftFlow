from fastapi import FastAPI
from app.api.v2 import api_router
from fastapi.middleware.cors import CORSMiddleware
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
