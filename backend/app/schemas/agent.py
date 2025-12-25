from pydantic import BaseModel

class FormatAgentBase(BaseModel):
    raw_text: str
    user_request: str
    
class FormatAgentResponse(BaseModel):
    stat: str
    html: str
    css: str