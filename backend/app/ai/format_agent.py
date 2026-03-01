from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END, START
from langgraph.constants import Send
from langchain_groq import ChatGroq
import json
import re
import subprocess
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv
from langsmith import traceable
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from app.db.style_db import StyleRetriever
import uuid

# --- ENV SETUP ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
env_path = project_root / "envs" / ".env"
load_dotenv(dotenv_path=env_path)

print(f"Loading env from: {env_path}")
print(f"API Key Found: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")

# --- LLM ---
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    streaming=False  # streaming=False for parallel chunk calls, avoids race conditions
)

# ============================================================
# STATE DEFINITIONS
# ============================================================

class ChunkState(TypedDict):
    """State for each individual chunk processed in parallel"""
    chunk: str        # The raw text chunk
    index: int        # Position in the original document

class AgentState(TypedDict):
    """Main graph state"""
    user_request: str
    raw_text: str
    chunks: List[str]                        # After chunking
    markdown_chunks: Annotated[list, lambda x, y: x + y]  # Reducer: collects all parallel results
    markdown_content: str                    # After stitching
    selected_theme: str                      # After style retrieval (JSON string)
    document_content: str                    # Final LaTeX output
    messages: Annotated[list, add_messages]


# ============================================================
# PROMPTS
# ============================================================

markdown_agent_instruction = """
You are the **Semantic Markdown Architect**.
Your goal is to convert a CHUNK of raw text into clean, valid GitHub Flavored Markdown with LaTeX support.

### RULES
1. **Formatting:** Use # for H1, ## for H2, etc. Use standard Markdown for lists and bold text.
2. **LaTeX Math:** Wrap all mathematical formulas in $..$ for inline and $$..$$ for blocks.
3. **No HTML:** Do not use any HTML tags.
4. **Preserve Structure:** Keep headings, paragraphs, and lists as they are — do not summarize.
5. **Chunk Awareness:** This is ONE chunk of a larger document. Do not add intro or conclusion.

### EXAMPLE
Input: "Einstein's theory. Energy equals mass times light squared."
Output: "## Einstein's Theory\nEnergy is defined by the formula: $$E = mc^2$$"
"""

markdown_prompt = ChatPromptTemplate.from_messages([
    ("system", markdown_agent_instruction),
    ("human", "Convert this chunk to Markdown:\n\n{chunk}")
])

markdown_generate = markdown_prompt | llm


# ============================================================
# NODE 1: CHUNKER
# Splits raw text into sections by heading or fixed size
# ============================================================

def chunker_node(state: AgentState):
    raw_text = state["raw_text"]
    
    # Split by headings (lines starting with a number+dot or all-caps or markdown #)
    # This is a smart split — keeps sections together
    section_pattern = re.compile(
        r'(?=(?:\n|^)(?:#{1,3}\s|\d+\.\s[A-Z]|[A-Z][A-Z\s]{4,}\n))',
        re.MULTILINE
    )
    
    sections = section_pattern.split(raw_text)
    
    # Filter empty chunks, strip whitespace
    chunks = [s.strip() for s in sections if s.strip()]
    
    # Safety: if regex found nothing useful, fallback to fixed-size chunking (1500 words)
    if len(chunks) <= 1:
        words = raw_text.split()
        chunk_size = 1500
        chunks = [
            " ".join(words[i:i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]
    
    print(f"[Chunker] Split document into {len(chunks)} chunks")
    
    return {
        "chunks": chunks,
        "markdown_chunks": []  # Initialize empty for the reducer
    }


# ============================================================
# NODE 2: CHUNK ROUTER (Send API — fans out in parallel)
# ============================================================

def chunk_router(state: AgentState):
    """
    Uses LangGraph Send() to fan out each chunk 
    to markdown_format_node in PARALLEL
    """
    return [
        Send("markdown_format", {"chunk": chunk, "index": i})
        for i, chunk in enumerate(state["chunks"])
    ]


# ============================================================
# NODE 3: MARKDOWN FORMAT (runs in parallel per chunk)
# ============================================================

@traceable
async def markdown_format_node(state: ChunkState):
    chunk = state["chunk"]
    index = state["index"]
    
    print(f"[Markdown Node] Processing chunk {index + 1}...")
    
    response = await markdown_generate.ainvoke({"chunk": chunk})
    
    print(f"[Markdown Node] Chunk {index + 1} done.")
    
    # Return as list with index so reducer can sort later
    return {
        "markdown_chunks": [{"index": index, "content": response.content}]
    }


# ============================================================
# NODE 4: REDUCER — Stitches all markdown chunks in order
# ============================================================

def reducer_node(state: AgentState):
    chunks = state["markdown_chunks"]
    
    # Sort by original index to maintain document order
    sorted_chunks = sorted(chunks, key=lambda x: x["index"])
    
    # Join with double newline for clean markdown separation
    full_markdown = "\n\n".join(c["content"] for c in sorted_chunks)
    
    print(f"[Reducer] Stitched {len(sorted_chunks)} chunks into full markdown.")
    
    return {
        "markdown_content": full_markdown
    }


# ============================================================
# NODE 5: STYLE RETRIEVAL (vector search — runs ONCE)
# ============================================================

@traceable
def style_retrieval_node(state: AgentState):
    retriever = StyleRetriever()
    user_query = state["user_request"]
    
    theme_data = retriever.search_style(user_query)
    
    if theme_data:
        name = theme_data.get("name")
        distance = theme_data.get("distance")
        print(f"[Style Retrieval] Found: {name} (Distance: {distance:.4f})")
    else:
        print("[Style Retrieval] No match found, using default.")
        theme_data = {
            "id": 1,
            "name": "Academic Standard",
            "preview_class": "theme-academic",
            "tex_template_path": "default.tex",
            "export_engine": "xelatex",
            "distance": 0.0
        }

    return {
        "selected_theme": json.dumps(theme_data)
    }


# ============================================================
# NODE 6: PANDOC CONVERSION (markdown + template → LaTeX)
# runs ONCE, deterministic, no LLM
# ============================================================

def pandoc_node(state: AgentState):
    markdown_content = state["markdown_content"]
    theme = json.loads(state["selected_theme"])
    
    engine = theme.get("export_engine", "xelatex")
    template_path = theme.get("tex_template_path", "default.tex")
    style_name = theme.get("name", "Academic Standard")
    
    print(f"[Pandoc] Converting to LaTeX | Style: {style_name} | Engine: {engine}")
    
    # Write markdown to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as md_file:
        md_file.write(markdown_content)
        md_path = md_file.name
    
    output_tex_path = md_path.replace(".md", ".tex")
    
    try:
        # Build pandoc command
        # Check if the .tex template actually exists, else use default pandoc latex
        templates_dir = project_root / "templates"
        full_template_path = templates_dir / template_path
        
        cmd = ["pandoc", md_path, "-o", output_tex_path, "--standalone"]
        
        if full_template_path.exists():
            cmd += [f"--template={full_template_path}"]
            print(f"[Pandoc] Using template: {full_template_path}")
        else:
            # Fallback: pandoc's built-in latex with basic vars
            cmd += [
                "-V", f"documentclass=article",
                "-V", "fontsize=12pt",
                "-V", "geometry=margin=1in",
            ]
            print(f"[Pandoc] Template not found, using pandoc default latex.")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"[Pandoc] Error: {result.stderr}")
            # Fallback: return raw markdown wrapped in minimal LaTeX
            latex_content = _minimal_latex_fallback(markdown_content, style_name)
        else:
            with open(output_tex_path, "r") as f:
                latex_content = f.read()
            print(f"[Pandoc] Conversion successful.")
    
    except FileNotFoundError:
        # Pandoc not installed
        print("[Pandoc] Pandoc not found on system. Using minimal LaTeX fallback.")
        latex_content = _minimal_latex_fallback(markdown_content, style_name)
    
    finally:
        # Cleanup temp files
        if os.path.exists(md_path):
            os.remove(md_path)
        if os.path.exists(output_tex_path):
            os.remove(output_tex_path)
    
    return {
        "document_content": latex_content
    }


def _minimal_latex_fallback(markdown: str, style_name: str) -> str:
    """
    If Pandoc is not installed or fails, 
    wrap markdown in a minimal compilable LaTeX document.
    """
    # Basic markdown → LaTeX conversions
    latex_body = markdown
    latex_body = re.sub(r'^# (.+)$', r'\\section{\1}', latex_body, flags=re.MULTILINE)
    latex_body = re.sub(r'^## (.+)$', r'\\subsection{\1}', latex_body, flags=re.MULTILINE)
    latex_body = re.sub(r'^### (.+)$', r'\\subsubsection{\1}', latex_body, flags=re.MULTILINE)
    latex_body = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', latex_body)
    latex_body = re.sub(r'\*(.+?)\*', r'\\textit{\1}', latex_body)
    latex_body = re.sub(r'^\- (.+)$', r'\\item \1', latex_body, flags=re.MULTILINE)
    latex_body = re.sub(r'\$\$(.+?)\$\$', r'\\[\1\\]', latex_body, flags=re.DOTALL)

    return f"""\\documentclass[12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}
\\usepackage{{times}}
\\title{{{style_name} Document}}
\\begin{{document}}
\\maketitle
{latex_body}
\\end{{document}}
"""


# ============================================================
# GRAPH WIRING
# ============================================================

builder = StateGraph(AgentState)

# Add all nodes
builder.add_node("chunker", chunker_node)
builder.add_node("markdown_format", markdown_format_node)
builder.add_node("reducer", reducer_node)
builder.add_node("style_node", style_retrieval_node)
builder.add_node("pandoc", pandoc_node)

# Wire edges
builder.add_edge(START, "chunker")

# Fan out: chunker → parallel markdown_format (via Send)
builder.add_conditional_edges("chunker", chunk_router, ["markdown_format"])

# Fan in: all parallel markdown_format → reducer
builder.add_edge("markdown_format", "reducer")

# Sequential after reduce
builder.add_edge("reducer", "style_node")
builder.add_edge("style_node", "pandoc")
builder.add_edge("pandoc", END)

memory = InMemorySaver()
app = builder.compile(checkpointer=memory)


# ============================================================
# ENTRY POINT
# ============================================================

@traceable
async def format_graph(raw_text: str, user_query: str):
    initial_inputs = {
        "raw_text": raw_text,
        "user_request": user_query,
        "messages": [],
        "markdown_chunks": [],  # Must initialize for the Annotated reducer
    }

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    print("🚀 Starting the Agent...")
    final_state = await app.ainvoke(initial_inputs, config=config)
    
    return {
        "markdown_content": final_state["markdown_content"],
        "selected_theme": final_state["selected_theme"],
        "latex_content": final_state["document_content"]  # Final LaTeX string
    }