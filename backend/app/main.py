from fastapi import FastAPI
from app.api.v2 import api_router
app = FastAPI()

@app.get("/")
def index_mesg():
    return {
        "message": "Use /docs endpoint for now"
    }
    


app.include_router(api_router, prefix="/api/v2")
