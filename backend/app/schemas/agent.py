from pydantic import BaseModel



class FormatAgentBase(BaseModel):
    raw_text: str
    doc_type: str
    
class FormatAgentResponse(BaseModel):
    stat: str
    html: str
    css: str