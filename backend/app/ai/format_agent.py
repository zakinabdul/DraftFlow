from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
#from app.core.config import settings
from langgraph.graph.message import add_messages
from pathlib import Path
import os
from dotenv import load_dotenv

# 1. Get the path to the current file (program.py)
current_file_path = Path(__file__).resolve()

# 2. Go up 3 levels to the root: 
#    Level 1: inside 'folder'
#    Level 2: inside 'app'
#    Level 3: project root (where 'envs' and 'app' live side-by-side)
project_root = current_file_path.parent.parent.parent

# 3. Point to the specific file
env_path = project_root / "envs" / ".env"

# 4. Load it explicitly
load_dotenv(dotenv_path=env_path)

# Debugging: Check if it worked
print(f"Loading env from: {env_path}")
print(f"API Key Found: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")

# --- Now run your LangChain code ---

# try local envs first, then try one level up (useful when notebook is inside "Trial")
"""env_path = Path("envs") / ".env"
if not env_path.exists():
    env_path = Path.cwd().parent / "envs" / ".env"

if not env_path.exists():
    raise FileNotFoundError(f".env not found (looked at {Path('envs')}, {env_path.resolve()})")

print("Using .env:", env_path.resolve())
groq_api = None
# Prefer python-dotenv if available, else fallback to simple parser
load_dotenv(dotenv_path=env_path)
# Support both GROQ_API_KEY (preferred) and legacy GROQ_API
groq_api = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API")

if not groq_api:
    raise RuntimeError(f"GROQ_API_KEY (or GROQ_API) not found in {env_path}")

# ensure the client library sees the key via the expected env var
os.environ["GROQ_API_KEY"] = groq_api

"""

# llm client connection
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    streaming=True
    )

# Agent state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    raw_text: str          # The input text
    doc_type: str          # e.g., "Business Report", "News Article"
    html_code: str         # Generated HTML
    css_code: str          # Generated CSS
    validation_status: str # "APPROVED" or "REJECTED"
    feedback: str          # Critique from the validator if rejected
    retry_count: int       # To prevent infinite loops
    last_error_source: str
    
# TODO: HTML formatting Agent

html_agent_instruction = """

You are the **Semantic HTML Architect** for a document generation pipeline.
              Your goal is to convert raw text into a strictly structured, valid HTML5 document 
              suitable for professional reports and articles.
              ### CRITICAL RULES
              1. **Semantic Hierarchy:** Analyze the text's flow to determine structure.
                 - First significant line → `<h1>` (Main Title)
                 - Major sections → `<h2>`
                 - Subsections → `<h3>`
                 - Body text → `<p>`
                 - Lists → `<ul>`/`<ol>` with `<li>`
              2. **Data Block IDs (Mandatory):** - Every single content element (h1-h6, p, li) must have a unique `data-block-id`.
                 - Format: `block-1`, `block-2`, `block-3` (strictly sequential, no gaps).
                 - Apply the ID directly to the tag (e.g., `<p data-block-id="block-4">`).
              3. **Content Integrity:** Do NOT summarize, rewrite, or delete any text. Preserve the original wording exactly.
              4. **Clean Output:** Return **ONLY** the raw HTML string. No markdown backticks (```), no CSS, no `<style>`, no conversational filler.
       
              ###  MAPPING LOGIC
              - **Emphasis:** Detect "Introduction", "Conclusion", or all-caps lines as headers.
              - **Formatting:** Convert *text* to `<em>` and **text** to `<strong>` if detected, but prioritize block structure.
       
              ###  FEW-SHOT EXAMPLE
              **Input:**
              "Quarterly Report
              Overview
              Sales were up 20%.
              - East Coast: Good
              - West Coast: Bad"
              
              **Output:**
              <!DOCTYPE html>
              <html>
              <body>
                <h1 data-block-id="block-1">Quarterly Report</h1>
                <h2 data-block-id="block-2">Overview</h2>
                <p data-block-id="block-3">Sales were up 20%.</p>
                <ul data-block-id="block-4">
                  <li data-block-id="block-5">East Coast: Good</li>
                  <li data-block-id="block-6">West Coast: Bad</li>
                </ul>
              </body>
              </html>"""
    
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


 ### TO test 
"""
 # Mock a fake initial state
initial_state = {
    "messages": [],
    "raw_text": "Title: My Report. Body: Sales are up.",
    "retry_count": 0
}

# Run the node manually
result_update = generate_html_node(initial_state)

print(f"Generated HTML: {result_update['html_code']}")
print(f"New Message History Length: {len(result_update['messages'])}")
 """

# TODO: CSS formatting agent   
    
    
css_agent_instruction =             """
        You are the **Print Media Styling Specialist**.
        Your goal is to generate professional, **PDF-ready CSS** that transforms semantic HTML into a document suitable for high-quality printing.
        
        ###  INPUT CONTEXT
        **Document Type:** {{ doc_type }} (e.g., Report, Article, Memo)
        **HTML Structure:** {{ html_code }}
        
        ### CRITICAL RULES
        1. **Paged Media is Mandatory:** You MUST start with the `@page` rule to define physical dimensions (A4/Letter) and margins (min 2cm).
        2. **Print Logic:** Wrap body styles in `@media print`. Ensure:
           - Backgrounds are white (`#fff`), Text is black (`#000`).
           - `font-size` is legible (11pt-12pt for body).
           - `line-height` is generous (1.4 - 1.6).
        3. **Break Control:**
           - Headings (`h1`-`h3`) must NEVER be at the bottom of a page (`page-break-after: avoid`).
           - Paragraphs should avoid widows/orphans (`orphans: 3; widows: 3`).
           - Tables/Images must not overflow the page width (`max-width: 100%`).
        4. **Style Matching:**
           - If 'Report': Use Serif fonts (Times, Georgia) and clean headers.
           - If 'Blog/Article': Use Sans-Serif (Helvetica, Arial) and modern headers.
        5. **Output Format:** Return **ONLY** the raw CSS string. No markdown backticks (```), no explanations.
        
        ### CRITIQUE HANDLING
        **Previous Feedback:** {{ feedback }}
        (If feedback exists, prioritize fixing the specific issue mentioned, e.g., "increase font size" or "fix margins".)
        
        ### EXAMPLE OUTPUT PATTERN
        @page { size: A4; margin: 2.5cm; }
        @media print {
          body { font-family: Georgia, serif; line-height: 1.5; color: #000; }
          h1 { font-size: 24pt; border-bottom: 2px solid #333; page-break-after: avoid; }
          p { margin-bottom: 1em; orphans: 3; widows: 3; }
          /* ...rest of code... */
        }
         """

# 2. Create the Prompt Template using Jinja2
css_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        css_agent_instruction, 
        template_format="jinja2" 
    ),
    # Optional: Add a human trigger to start the generation
    HumanMessagePromptTemplate.from_template("Generate the CSS now.")
])
         
"""css_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            template_text, 
            template_format="jinja2"  # <--- THIS FIXES THE ERROR
        ),
        MessagesPlaceholder(variable_name="messages")
    ]
)"""


# 4. Run the Chain
chain = css_prompt | llm

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
        "doc_type": state["doc_type"] 
    })
    
    return {
        "css_code": response.content,
        "messages": [response]
    }
    
# TODO: Validating Agent
    
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

import json
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

# 1. Setup Prompt with Jinja2
validator_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        validator_agent_instruction, 
        template_format="jinja2"
    )
])

# 2. The Node Function (Python Logic)
async def validator_node(state: AgentState):
    print("--- VALIDATING OUTPUT ---")
    
    # Run the Chain
    chain = validator_prompt | llm
    
    response = await chain.ainvoke({
        "doc_type": state["doc_type"],
        "html_code": state["html_code"],
        "css_code": state["css_code"]
    })
    
    # Parse the JSON string from the LLM
    try:
        # Some LLMs might wrap JSON in ```json ... ```. This cleans it.
        content = response.content if isinstance(response.content, str) else str(response.content)
        clean_content = content.strip().replace("```json", "").replace("```", "")
        result_json = json.loads(clean_content)
    except json.JSONDecodeError:
        # Fallback if LLM messes up JSON
        result_json = {"status": "REJECTED", "error_source": "CSS_AGENT", "feedback": "JSON Parsing Failed. Retry."}

    # Update State
    return {
        "validation_status": result_json["status"],
        "feedback": result_json["feedback"],
        # We can also store 'error_source' to make the Router's job easier
        "last_error_source": result_json.get("error_source")
    }
    """
def should_continue(state):
    if state["validation_status"] == "APPROVED":
        return END
    
    # If the Validator explicitly blamed the HTML Agent...
    if state["last_error_source"] == "HTML_AGENT":
        return "html_agent"
        
    # Default to CSS Agent for style issues
    return "css_agent"""

from langgraph.graph import END

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

builder = StateGraph(AgentState)
builder.add_node("html_format", generate_html_node)
builder.add_node("css_format", css_agent_node)
builder.add_node("validator", validator_node)
builder.add_edge(START, "html_format")
builder.add_edge("html_format", "css_format")
builder.add_edge("css_format", "validator")
builder.add_conditional_edges(
    "validator",          # 1. Who is asking? (The Source Node)
    should_continue,      # 2. Who decides? (The Function)
    
    # 3. The Map: { "Return_Value": "Actual_Node_Name" }
    {
        END: END,
        "html_format": "html_format",
        "css_format": "css_format"
    }
)
from langgraph.checkpoint.memory import InMemorySaver
memory = InMemorySaver()
app = builder.compile(checkpointer=memory)

# to test the app
async def format_graph(raw_text: str, doc_type:str):
    # 1. Define your inputs exactly as they appear in AgentState
    initial_inputs = {
        "raw_text": raw_text,
        "doc_type": doc_type,
        "messages": [],     # Initialize empty chat history
        "retry_count": 0     # Start at zero
    }

    # 2. Define a configuration (Required for checkpointer to track this "thread")
    # You can change the "thread_id" for different users or different documents.
    config = {"configurable": {"thread_id": "doc_run_001"}}

    # 3. Run the Graph
    print("🚀 Starting the Agent...")
    final_state = await app.ainvoke(initial_inputs, config=config) # type: ignore

    # 4. Access the Results
    # print("\n--- FINAL OUTPUT ---")
    # print(f"Status: {final_state['validation_status']}")
    # print(f"HTML Code:\n{final_state['html_code'][:200]}...") # Printing first 200 chars
    # print(f"CSS Code:\n{final_state['css_code'][:200]}...")   # Printing first 200 chars
    return {
        "stat": final_state['validation_status'],
        "html": final_state['html_code'],
        "css" : final_state['css_code']  
    }

"""if __name__ == "__main__":
    import asyncio
    asyncio.run(format_graph())"""