from pydantic import BaseModel

class FormatAgentBase(BaseModel):
    raw_text: str
    user_request: str
    
class FormatAgentResponse(BaseModel):
    code: str