from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
import json
#from app.core.config import settings
from langgraph.graph.message import add_messages
from pathlib import Path
import os
from dotenv import load_dotenv
from langsmith import traceable
from app.db.style_db import StyleRetriever
from langgraph.checkpoint.memory import InMemorySaver

# 1. Get the path to the current file (program.py)
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
env_path = project_root / "envs" / ".env"
# 4. Load it explicitly
load_dotenv(dotenv_path=env_path)

# Debugging: Check if it worked
print(f"Loading env from: {env_path}")
print(f"API Key Found: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")

# llm client connection
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    streaming=True
    )

# Agent state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_request: str
    raw_text: str          # The input text
    doc_type: str          # e.g., "Business Report", "News Article"
    ref_html : str
    ref_css: str
    html_code: str         # Generated HTML
    css_code: str          # Generated CSS
    validation_status: str # "APPROVED" or "REJECTED"
    feedback: str          # Critique from the validator if rejected
    retry_count: int       # To prevent infinite loops
    last_error_source: str
    merged_code: str
    
# TODO: HTML formatting Agent
html_agent_instruction = """

You are the **Semantic HTML Architect** for a document generation pipeline.
Your goal is to convert raw text into a strictly structured HTML5 fragment.

### CRITICAL RULES

1. **Attribute Formatting (Crucial):**
   - You MUST use **SINGLE QUOTES** (') for all HTML attributes.
   - CORRECT: <div class='page-container'>
   - WRONG: <div class="page-container">
   - This is required to prevent JSON escaping issues.

2. **Required Structure:**
   - Return **ONLY** the HTML string. Do not use markdown blocks or descriptive text.
   - Your output must follow this exact pattern:
     <body><div class='page-container'>{{CONTENT_HERE}}</div></body>

3. **Semantic Hierarchy:**
   - First significant line → <h1>
   - Major sections → <h2>
   - Subsections → <h3>
   - Body text → <p>
   - Lists → <ul>/<ol> with <li>

4. **Data Block IDs (Mandatory):**
   - Every single content element (h1-h6, p, li) must have a unique `data-block-id`.
   - Format: `block-1`, `block-2` (strictly sequential).
   - Example: <p data-block-id='block-4'>

5. **Pure HTML Only:**
   - **NO** <style> tags.
   - **NO** <head> tags.
   - **NO** <!DOCTYPE> declarations.
   - **NO** CSS.

### FEW-SHOT EXAMPLE

**Input:**
"Quarterly Report
Overview
Sales were up 20%.
- East Coast: Good
- West Coast: Bad"

**Output:**
<body><div class='page-container'><h1 data-block-id='block-1'>Quarterly Report</h1><h2 data-block-id='block-2'>Overview</h2><p data-block-id='block-3'>Sales were up 20%.</p><ul data-block-id='block-4'><li data-block-id='block-5'>East Coast: Good</li><li data-block-id='block-6'>West Coast: Bad</li></ul></div></body>
"""
    
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,SystemMessagePromptTemplate, HumanMessagePromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", html_agent_instruction
        ),
        # used for conversation history
        MessagesPlaceholder(variable_name="messages"),
        # The New Input (The raw text you want to convert)
    ("human", "Here is the raw text to convert:\n\n {raw_text}")
    ]
) 

generate = prompt | llm



@traceable
async def generate_html_node(state: AgentState):
    """
     Takes the raw_text and convert to html_code
    """
    print("===Generating HTML=====")
    # Get the input from state
    current_messages = state["messages"]
    raw_input = state["raw_text"]
    
    # Invoke the llm
    response = await generate.ainvoke({
        "messages":current_messages,
        "raw_text": raw_input
    })
    
    # return the results
    
    return {
        "html_code": response.content,
        "messages": [response],
        "retry_count": state.get("retry_count",0)+1
    }


@traceable
def style_retrival_node(state: AgentState):
    '''
    Fetch the prefered style from the user query in vector db
    '''
    retriever = StyleRetriever()
    user_query = state["user_request"]
    result = retriever.search_style_name(user_query)
    if result:
        name, distance = result
        print(f"Found Style: {name} (Distance: {distance:.4f})")
        ref= retriever.search_css_html(name)
        return {
        'doc_type': name,
        'ref_html': ref[1],
        'ref_css' : ref[0]
            
        }
        
    else:
        print("Error finding the vector name")
        
                
# TODO: CSS formatting agent   
    
css_agent_instruction = """
        You are the **CSS Architecture Specialist**.
        Your goal is to output **Production-Ready CSS** by strictly adapting a Reference Template to a specific HTML structure.
        
        ### INPUT CONTEXT
        **Document Type:** {{ doc_type }}
        **Reference CSS:** {{ ref_css }} (THE SOURCE OF TRUTH)
        **Reference HTML:** {{ ref_html }} (Use this to identify wrapper class names like .page-container)
        **Target HTML:** {{ html_code }} (The content to be styled)
        **User Feedback:** {{ feedback }}
        
        ### CRITICAL INSTRUCTIONS
        1. **Strict Architecture Adherence:**
           You MUST preserve the 3-layer "Preview-to-Print" workflow found in the Reference CSS:
           - **Layer 1 (Global):** Typography & Layout.
           - **Layer 2 (@media screen):** The "Paper Simulation" (grey background, shadows, fixed width containers).
           - **Layer 3 (@media print):** The "Print Reset" (white background, no shadows, 100% width, margins controlled by @page).
        
        2. **Smart Adaptation:**
           - Analyze {{ ref_html }} to find the main wrapper class (e.g., `.page-container` or `.content-wrapper`).
           - Ensure the CSS correctly targets the wrapper found in {{ html_code }}.
           - If {{ html_code }} contains elements (like `<table>`, `<code>`, `<blockquote>`) not covered in {{ ref_css }}, generate consistent styles for them that match the document's theme.
        3. **Feedback Handling:**
           - If {{ feedback }} is empty, return {{ ref_css }} with only necessary structural adaptations for the HTML.
           - If {{ feedback }} exists, apply the changes *within* the existing architecture (e.g., if asked to change margins, update the `@page` block, not the body).
        
        4. **Output Rules:**
           - Return **ONLY** the valid CSS string.
           - NO markdown formatting (```css).
           - NO explanations.
        5. **Container Wrapper Mandate:**
             Your CSS architecture MUST rely on a wrapper class (like .page-container) to define the paper's dimensions. In @media screen, the body must act ONLY as a flex-parent to center this wrapper. You must NEVER apply 'display: flex' to the body unless you are certain a single wrapper div exists to hold all content.
        """

css_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        css_agent_instruction, 
        template_format="jinja2" 
    ),
    # Optional
    HumanMessagePromptTemplate.from_template("Generate the CSS now.")
])
         
# 4. Run the Chain
chain = css_prompt | llm

@traceable
async def css_agent_node(state: AgentState):
    """
    Here it takes the html code and generate suitable css styles
    """
    print("-----CSS Generating------")
    # get the inputs
    html_code = state["html_code"]
    current_feedback = state.get("feedback", "")
    response = await chain.ainvoke({
        "html_code": html_code,
        "feedback": current_feedback,
        "doc_type": state["doc_type"] ,
        "ref_css" : state["ref_css"],
        "ref_html" : state["ref_html"]
    })
    
    return {
        "css_code": response.content,
        "messages": [response]
    }
    
# TODO: Validating Agent
    
# Need to rethink wheather the validator is needed or not
validator_agent_instruction = """
You are the **Document Compliance & QA Lead**. 
Your job is to rigorously audit the generated HTML and CSS to ensure they meet the strict standards for automated PDF generation.

### 📥 INPUT DATA
**Document Type:** {{ doc_type }}
**HTML Code:** {{ html_code }}
**CSS Code:** {{ css_code }}

### ✅ VALIDATION CHECKLIST (Pass/Fail Criteria)

**1. HTML Structural Integrity:**
   - [ ] Is the HTML valid with no unclosed tags?
   - [ ] Do **ALL** meaningful tags (h1-h6, p, li) contain the `data-block-id` attribute? (CRITICAL)
   - [ ] Is the content hierarchy logical for a {{ doc_type }}?

**2. CSS Print Compliance:**
   - [ ] Does the CSS contain a valid `@page` rule defining margins and size?
   - [ ] Is there an `@media print` block?
   - [ ] Are font sizes defined in print-friendly units (pt) or legible px?
   - [ ] Is the contrast high (black text/white background)?

### 📝 OUTPUT FORMAT
You must return a **Single JSON Object** (no markdown formatting, no explanations outside the JSON).

**JSON Schema:**
{
  "status": "APPROVED" | "REJECTED",
  "error_source": "HTML_AGENT" | "CSS_AGENT" | null,
  "feedback": "Precise instructions on what to fix. If APPROVED, leave empty."
}

### 💡 DECISION LOGIC
- If `data-block-id`s are missing -> **REJECT** (Source: HTML_AGENT).
- If `@page` is missing or colors are bad -> **REJECT** (Source: CSS_AGENT).
- If the design looks ugly but technically passes -> **REJECT** (Source: CSS_AGENT).
- If perfect -> **APPROVED**.

### ⚡ EXAMPLE OUTPUTS
**Example 1 (Fail):**
{
  "status": "REJECTED",
  "error_source": "HTML_AGENT",
  "feedback": "Critical failure: <p> tags are missing data-block-id attributes. Rescan document and apply IDs sequentially."
}

**Example 2 (Pass):**
{
  "status": "APPROVED",
  "error_source": null,
  "feedback": ""
}
"""


# IMP: Currently Stopping usage of Validator for testing
"""import json
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

validator_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        validator_agent_instruction, 
        template_format="jinja2"
    )
])

@traceable
async def validator_node(state: AgentState):
    print("--- VALIDATING OUTPUT ---")
    
    # Run the Chain
    chain = validator_prompt | llm
    
    response = await chain.ainvoke({
        "doc_type": state["doc_type"],
        "html_code": state["html_code"],
        "css_code": state["css_code"]
    })
    
    # Parse the JSON string from the LLM and clean it
    try:
        content = response.content if isinstance(response.content, str) else str(response.content)
        clean_content = content.strip().replace("```json", "").replace("```", "")
        result_json = json.loads(clean_content)
    except json.JSONDecodeError:
        result_json = {"status": "REJECTED", "error_source": "CSS_AGENT", "feedback": "JSON Parsing Failed. Retry."}

    # Update State
    return {
        "validation_status": result_json["status"],
        "feedback": result_json["feedback"],
        # We can also store 'error_source' to make the Router's job easier
        "last_error_source": result_json.get("error_source")
    }
"""
"""
@traceable
def should_continue(state: AgentState):
    # 1. Check if we are done
    if state["validation_status"] == "APPROVED":
        return END  # This goes to the "Final Output" green box
    
    # 2. Check if we are stuck in a loop (Safety Guard)
    if state["retry_count"] > 3:
        return END  # Force finish to prevent infinite billable loops
        
    # 3. Route based on WHO made the mistake
    # (This matches the red arrows in your diagram)
    error_source = state.get("last_error_source", "UNKNOWN")
    
    if error_source == "CSS_AGENT":
        return "css_format"  # Go back only to CSS step
        
    else: 
        # Default to HTML if it's a structural error or unknown
        return "html_format"

"""

#
def merge_html_css(html_content: str, css_content: str) -> str:
    """Merges CSS into HTML head safely."""
    # Create the style block
    style_block = f"<style>{css_content}</style>"
    
    # Scenario 1: <head> tag exists -> Inject inside
    if "<head>" in html_content:
        merged_html = html_content.replace("</head>", f"{style_block}</head>")
        
    # Scenario 2: <html> exists but NO <head> (Your example fits here)
    elif "<html>" in html_content:
        # Create a head tag and inject it right after <html> opens
        merged_html = html_content.replace("<html>", f"<html><head>{style_block}</head>")
        
    # Scenario 3: Fragment only (No <html> or <body>)
    else:
        merged_html = f"<!DOCTYPE html><html><head>{style_block}</head><body>{html_content}</body></html>"
        
    return merged_html

@traceable
def merge_node(state: AgentState):
    # removing \n from the response
    html = state["html_code"].replace('\\"', '"').replace("\n", "")
    css = state["css_code"].replace("\n", "")
    result = merge_html_css(html_content=html, css_content=css)
    return {
        "merged_code": result
    }
    
# LangGraph Building 
builder = StateGraph(AgentState)
builder.add_node("html_format", generate_html_node)
builder.add_node("retrival_node", style_retrival_node)
builder.add_node("css_format", css_agent_node)
builder.add_node("merger", merge_node)
builder.add_edge(START, "html_format")
builder.add_edge("html_format", "retrival_node")
builder.add_edge("retrival_node", "css_format")
builder.add_edge("css_format", "merger")
"""builder.add_conditional_edges(
    "validator",          # (The Source Node)
    should_continue,      # Who decides? (The Function)
    
    # The Map: { "Return_Value": "Actual_Node_Name" }
    {
        END: END,
        "html_format": "html_format",
        "css_format": "css_format"
    }
)
"""
memory = InMemorySaver()
app = builder.compile(checkpointer=memory)

# App main function
@traceable
async def format_graph(raw_text: str, user_query:str):
    # inputs  for AgentState intial start
    initial_inputs = {
        "raw_text": raw_text,
        "user_request": user_query,
        "messages": [],     
        "retry_count": 0     
    }

    # You can change the "thread_id" for different users or different documents.
    config = {"configurable": {"thread_id": "doc_run_001"}}

    # 3. Run the Graph
    print("🚀 Starting the Agent...")
    final_state = await app.ainvoke(initial_inputs, config=config) # type: ignore
    return {
       "code": final_state['merged_code']
    }

    """# removing \n from the response
    final_state["html_code"] = final_state["html_code"].replace("\n", "")
    final_state["css_code"] = final_state["css_code"].replace("\n", "")"""
    """return {
        "stat": final_state['validation_status'],
        "html": final_state['html_code'],
        "css" : final_state['css_code']  
    }
"""
"""if __name__ == "__main__":
    import asyncio
    asyncio.run(format_graph())"""