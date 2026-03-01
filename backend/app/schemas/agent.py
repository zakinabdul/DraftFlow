from pydantic import BaseModel
class FormatAgentBase(BaseModel):
    raw_text: str
    user_request: str
class FormatAgentResponse(BaseModel):
    markdown_content: str
    selected_theme: str
    latex_content: str