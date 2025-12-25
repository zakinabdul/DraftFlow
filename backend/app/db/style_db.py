import sqlite3
import sqlite_vec
import struct
import os
# NEW IMPORT:
from google import genai
from typing import List
from typing import List
from dotenv import load_dotenv
from pathlib import Path

# --- CONFIGURATION ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
env_path = project_root / "envs" / ".env"
# Load environment variables
load_dotenv(dotenv_path=env_path)

# Get API key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable.")

# Debugging: Check if it worked
print(f"Loading env from: {env_path}")
print(f"API Key Found: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")

# --- TEMPLATES ---
STYLE_TEMPLATES = [
    {
        "id": 1,
        "name": "Academic Standard",
        "description": "Professional academic paper style, Times New Roman, double spacing. Best for research papers and thesis.",
        "css": "/* SHARED */ body { font-family: 'Times New Roman', serif; line-height: 2.0; font-size: 12pt; color: #000; margin: 0; } h1 { text-align: center; font-size: 16pt; margin-bottom: 24pt; } p { text-indent: 0.5in; margin-bottom: 0; } /* SCREEN PREVIEW */ @media screen { body { background: #525659; display: flex; justify-content: center; padding: 40px 0; } .page-container { background: white; width: 210mm; min-height: 297mm; padding: 2.54cm; box-shadow: 0 0 10px rgba(0,0,0,0.5); box-sizing: border-box; } } /* PRINT EXPORT */ @media print { @page { size: A4; margin: 2.54cm; } body { background: none; display: block; } .page-container { width: 100%; margin: 0; padding: 0; box-shadow: none; } }",
        "html": "<!DOCTYPE html><html><body><div class='page-container'><h1>{{title}}</h1><div class='content'>{{content}}</div></div></body></html>"
    },
    {
        "id": 2,
        "name": "Modern Startup",
        "description": "Clean, minimalist, sans-serif design. Good for business proposals and startup pitches.",
        "css": "/* SHARED */ body { font-family: 'Helvetica', 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; } h1 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; } h2 { color: #1e40af; margin-top: 20px; } p { margin-bottom: 15px; } /* SCREEN PREVIEW */ @media screen { body { background: #525659; display: flex; justify-content: center; padding: 40px 0; } .page-container { background: white; width: 210mm; min-height: 297mm; padding: 2cm; box-shadow: 0 0 10px rgba(0,0,0,0.5); box-sizing: border-box; } } /* PRINT EXPORT */ @media print { @page { size: A4; margin: 2cm; } body { background: none; display: block; } .page-container { width: 100%; margin: 0; padding: 0; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }",
        "html": "<!DOCTYPE html><html><body><div class='page-container'><header><h1>{{title}}</h1></header><main>{{content}}</main></div></body></html>"
    },
    {
        "id": 3,
        "name": "Creative Blog",
        "description": "Colorful, airy, and casual. Good for creative writing. High contrast and larger fonts.",
        "css": "/* SHARED */ body { font-family: 'Georgia', serif; font-size: 14pt; color: #2c3e50; margin: 0; } h1 { font-family: 'Courier New', monospace; color: #e67e22; text-transform: uppercase; } .content { padding: 20px; border-left: 5px solid #e67e22; } /* SCREEN PREVIEW */ @media screen { body { background: #525659; display: flex; justify-content: center; padding: 40px 0; } .page-container { background-color: #fdfbf7; width: 210mm; min-height: 297mm; padding: 1.5cm; box-shadow: 0 0 10px rgba(0,0,0,0.5); box-sizing: border-box; } } /* PRINT EXPORT */ @media print { @page { size: A4; margin: 1.5cm; } body { background: none; display: block; } .page-container { width: 100%; margin: 0; padding: 0; box-shadow: none; background-color: #fdfbf7; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }",
        "html": "<!DOCTYPE html><html><body><div class='page-container'><h1>{{title}}</h1><div class='content'>{{content}}</div></div></body></html>"
    },
    {
        "id": 4,
        "name": "Executive Board Report",
        "description": "Highly structured layout with a visible border. Features a dark header strip. Perfect for official summaries.",
        "css": "/* SHARED */ body { font-family: 'Segoe UI', 'Roboto', sans-serif; color: #1a1a1a; line-height: 1.5; margin: 0; } h1 { background-color: #1a1a1a; color: #fff; padding: 15px; text-transform: uppercase; font-size: 18pt; margin: -40px -40px 30px -40px; text-align: center; letter-spacing: 2px; } h2 { border-left: 5px solid #d93025; padding-left: 10px; margin-top: 30px; font-size: 14pt; } p { text-align: justify; margin-bottom: 15px; } /* SCREEN PREVIEW */ @media screen { body { background: #525659; display: flex; justify-content: center; padding: 40px 0; } .page-container { background: white; width: 210mm; min-height: 297mm; padding: 40px; border: 2px solid #333; box-shadow: 0 0 10px rgba(0,0,0,0.5); box-sizing: border-box; } } /* PRINT EXPORT */ @media print { @page { size: A4; margin: 1.5cm; } body { background: none; display: block; } .page-container { width: 100%; margin: 0; padding: 0; border: 2px solid #333; height: 98%; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }",
        "html": "<!DOCTYPE html><html><body><div class='page-container'><h1>{{title}}</h1><div class='main-content'>{{content}}</div></div></body></html>"
    },
    {
        "id": 5,
        "name": "Scientific Journal (Two-Column)",
        "description": "Classic research paper look. Two-column layout and serif fonts. Ideal for IEEE-style reports.",
        "css": "/* SHARED */ body { font-family: 'Times New Roman', serif; line-height: 1.4; color: #000; font-size: 10pt; margin: 0; } h1 { font-size: 20pt; text-align: center; margin-bottom: 10px; font-weight: bold; line-height: 1.2; } .abstract { font-style: italic; margin: 0 auto 30px auto; width: 80%; text-align: center; color: #444; } .columns { column-count: 2; column-gap: 1cm; column-rule: 1px solid #ddd; text-align: justify; } h2 { font-size: 12pt; text-transform: uppercase; border-bottom: 1px solid #000; margin-top: 20px; padding-bottom: 5px; break-after: avoid; } /* SCREEN PREVIEW */ @media screen { body { background: #525659; display: flex; justify-content: center; padding: 40px 0; } .page-container { background: white; width: 210mm; min-height: 297mm; padding: 2cm; box-shadow: 0 0 10px rgba(0,0,0,0.5); box-sizing: border-box; } } /* PRINT EXPORT */ @media print { @page { size: A4; margin: 2cm; } body { background: none; display: block; } .page-container { width: 100%; margin: 0; padding: 0; box-shadow: none; } }",
        "html": "<!DOCTYPE html><html><body><div class='page-container'><h1>{{title}}</h1><p class='abstract'><strong>Abstract:</strong> This document represents a generated research report.</p><div class='columns'>{{content}}</div></div></body></html>"
    },
    {
        "id": 6,
        "name": "Technical Documentation",
        "description": "Developer-friendly style. Uses monospace fonts, grey backgrounds for sections. Good for code specs.",
        "css": "/* SHARED */ body { font-family: 'Consolas', 'Monaco', monospace; font-size: 10pt; color: #333; line-height: 1.6; margin: 0; } h1 { border-bottom: 4px solid #000; font-size: 22pt; padding-bottom: 10px; margin-bottom: 30px; } h2 { background-color: #f0f0f0; padding: 8px; border-left: 4px solid #007acc; margin-top: 30px; font-family: 'Segoe UI', sans-serif; } p { margin-bottom: 15px; } strong { color: #007acc; } /* SCREEN PREVIEW */ @media screen { body { background: #525659; display: flex; justify-content: center; padding: 40px 0; } .page-container { background: white; width: 210mm; min-height: 297mm; padding: 2.54cm; box-shadow: 0 0 10px rgba(0,0,0,0.5); box-sizing: border-box; } } /* PRINT EXPORT */ @media print { @page { size: A4; margin: 2.54cm; } body { background: none; display: block; } .page-container { width: 100%; margin: 0; padding: 0; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }",
        "html": "<!DOCTYPE html><html><body><div class='page-container'><h1>{{title}}</h1><main>{{content}}</main></div></body></html>"
    }
]

# --- GEMINI WRAPPER ---
class GeminiEmbedding:
    def __init__(self, model_name: str = "models/text-embedding-004"):
        self.model_name = model_name
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # NEW METHOD CALL:
        result = self.client.models.embed_content(
            model=self.model_name,
            contents=[{"text": text} for text in texts],
            config={
                "task_type": "retrieval_document",
                "title": "Style Description"
            }
        )
        # The new SDK returns objects, we extract the vectors:
        if result.embeddings is None:
            return []
        return [entry.values for entry in result.embeddings if entry.values is not None]
    
    def embed_query(self, text: str) -> List[float]:
        # NEW METHOD CALL:
        result = self.client.models.embed_content(
            model=self.model_name,
            contents={"text": text},
            config={
                "task_type": "retrieval_query"
            }
        )
        # Extract single vector:
        if result.embeddings is None or len(result.embeddings) == 0:
            return []
        values = result.embeddings[0].values
        return values if values is not None else []
# --- RETRIEVER CLASS ---
def serialize_float32(vector):
    """Helper to convert list of floats to binary format for SQLite"""
    return struct.pack(f"{len(vector)}f", *vector)

class StyleRetriever:
    def __init__(self):
        self.embedder = GeminiEmbedding()
        
        # Initialize in-memory SQLite DB
        self.db = sqlite3.connect(":memory:") 
        self.db.enable_load_extension(True)
        sqlite_vec.load(self.db)
        self.db.enable_load_extension(False)
        
        # 1. Create Virtual Table
        # Gemini text-embedding-004 uses 768 dimensions (not 1536)
        self.db.execute("""
            CREATE VIRTUAL TABLE styles USING vec0(
                id INTEGER PRIMARY KEY,
                embedding float[768],
                name TEXT,
                description TEXT,
                +css TEXT,
                +html TEXT
            )
        """)
        
        # 2. Populate DB
        self._populate_initial_data()

    def _populate_initial_data(self):
        print("Populating database with styles...")
        
        # Prepare text for embedding (Name + Description)
        descriptions = [f"{t['name']}. {t['description']}" for t in STYLE_TEMPLATES]
        
        # Batch embed using Gemini
        # Note: 'embed_content' accepts a list of strings for batching
        embeddings = self.embedder.embed_documents(descriptions)

        # Insert into SQLite
        for i, template in enumerate(STYLE_TEMPLATES):
            vector = embeddings[i]
            
            # Minify CSS (remove newlines) for cleaner storage
            clean_css = template["css"].replace("\n", "").strip()
            
            self.db.execute(
                "INSERT INTO styles(id, embedding, name, description, css, html) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    template["id"],
                    serialize_float32(vector),
                    template["name"],
                    template["description"],
                    clean_css,
                    template["html"]
                )
            )
        print(f"Successfully populated {len(STYLE_TEMPLATES)} styles.")

    def search_style_name(self, user_query, limit=1):
        # 1. Embed user query
        query_vector = self.embedder.embed_query(user_query)
        
        # 2. Perform Vector Search
        cursor = self.db.execute("""
            SELECT name, distance
            FROM styles
            WHERE embedding MATCH ?
            AND k = ?
            ORDER BY distance
        """, (serialize_float32(query_vector), limit))
        
        return cursor.fetchone()
    
    def search_css_html(self, name):
    # No vector search needed. Just a standard DB lookup.
        cursor = self.db.execute("""
            SELECT css, html
            FROM styles
            WHERE name = ?
        """, (name,))  # Pass 'name' as a tuple
        
        return cursor.fetchone()


# --- USAGE EXAMPLE ---
"""if __name__ == "__main__":
    # Initialize the retriever (this creates the DB and embeds templates)
    retriever = StyleRetriever()
    
    # Simulate a user request
    user_request = "I want a very formal look for a university paper"
    print(f"\nUser Query: '{user_request}'")
    
    result = retriever.search_style_name(user_request)
    
    if result:
        name,distance = result
        print(f"Found Style: {name} (Distance: {distance:.4f})")
        ref_css = retriever.search_css_html(name)
        print(ref_css[1])
    else:
        print("No style found.")"""