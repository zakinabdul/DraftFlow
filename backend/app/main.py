from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index_mesg():
    return {
        "message": "Use /docs endpoint for now"
    }
    
