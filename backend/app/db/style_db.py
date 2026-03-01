import sqlite3
import sqlite_vec
import struct
import os
# NEW IMPORT: try genai (new package) then fallback to generativeai (deprecated package)
try:
    import google.genai as genai
except Exception:
    try:
        import google.generativeai as genai
    except Exception as e:
        raise ImportError("Missing Google GenAI package: install 'google-genai' or 'google-generativeai'.") from e

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

# --- MODERN STYLE TEMPLATES ---
# These are designed to work with TipTap (Frontend) and Pandoc (Backend)
MODERN_STYLE_TEMPLATES = [
    {
        "id": 1,
        "name": "Academic Standard",
        "category": "Academic",
        # Used by TipTap wrapper to style the editor area
        "preview_class": "theme-academic", 
        "description": "Standard university format, Times New Roman, 12pt.",
        # Configuration for the Pandoc engine on export
        "export_config": {
            "engine": "xelatex",
            "mainfont": "Times New Roman",
            "fontsize": "12pt",
            "geometry": "margin=1in",
            "toc": False
        }
    },
    {
        "id": 4,
        "name": "IEEE Research Paper",
        "category": "Professional",
        "preview_class": "theme-ieee",
        "description": "Two-column technical format with LaTeX math support.",
        "export_config": {
            "engine": "pdflatex",
            "template": "ieee_template.tex", # You store this .tex file on your FastAPI server
            "columns": 2,
            "math": "katex"
        }
    },
    {
        "id": 2,
        "name": "College Project Report",
        "category": "Educational",
        "preview_class": "theme-college-report",
        "description": "Includes Cover Page and Table of Contents.",
        "export_config": {
            "engine": "xelatex",
            "toc": True,
            "template": "college_report_v2.tex",
            "metadata_fields": ["college_name", "department", "guide_name"]
        }
    }
]
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
    "name": "College Project Report",
    "description": "Professional academic report format with cover page, certificate, acknowledgement, and structured chapters. Perfect for engineering and science project documentation.",
    "css": "/* SHARED */ * { margin: 0; padding: 0; box-sizing: border-box; } body { font-family: 'Times New Roman', Times, serif; line-height: 1.6; color: #000; } .college-logo { margin: 0 auto 20px; width: 80px; height: 80px; border: 2px solid #000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14pt; } .college-name { font-size: 18pt; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 1px; text-align: center; } .department-name { font-size: 14pt; margin-bottom: 40px; text-align: center; } .cover-page { display: flex; flex-direction: column; justify-content: space-between; min-height: 247mm; text-align: center; } .report-label { font-size: 12pt; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; } .project-title { font-size: 20pt; font-weight: bold; text-transform: uppercase; margin: 20px 0; line-height: 1.4; border-top: 3px double #000; border-bottom: 3px double #000; padding: 20px 0; } .student-info { margin: 20px auto; max-width: 400px; } .student-row { display: flex; justify-content: space-between; margin: 8px 0; padding: 5px 0; border-bottom: 1px dotted #666; } .guide-section { margin-top: 30px; font-size: 11pt; } .guide-name { font-weight: bold; margin-top: 10px; } .submission-details { font-size: 11pt; } .academic-year { margin-top: 15px; font-weight: bold; } .certificate-title { font-size: 18pt; font-weight: bold; text-align: center; text-transform: uppercase; text-decoration: underline; margin-bottom: 30px; } .certificate-content { font-size: 12pt; text-align: justify; line-height: 2; margin-bottom: 40px; } .signature-section { display: flex; justify-content: space-between; margin-top: 80px; } .signature-line { border-top: 1px solid #000; width: 200px; margin: 60px auto 10px; } .section-title { font-size: 16pt; font-weight: bold; text-align: center; text-transform: uppercase; margin-bottom: 25px; text-decoration: underline; } .toc-item { display: flex; justify-content: space-between; margin: 12px 0; font-size: 12pt; } .toc-title { flex: 1; } .toc-dots { flex: 1; border-bottom: 1px dotted #000; margin: 0 10px; height: 1em; } .toc-page-num { width: 30px; text-align: right; } .toc-chapter { font-weight: bold; margin-top: 15px; } .toc-section { padding-left: 20px; } .chapter-title { font-size: 16pt; font-weight: bold; text-align: center; text-transform: uppercase; margin-bottom: 5px; } .chapter-name { font-size: 18pt; font-weight: bold; text-align: center; margin-bottom: 25px; text-transform: uppercase; } .section-heading { font-size: 14pt; font-weight: bold; margin: 25px 0 12px 0; } .subsection-heading { font-size: 12pt; font-weight: bold; margin: 20px 0 10px 0; font-style: italic; } p { font-size: 12pt; text-align: justify; margin-bottom: 12px; } ul, ol { margin: 12px 0 12px 40px; font-size: 12pt; } li { margin-bottom: 8px; } .figure, .table-container { margin: 20px 0; text-align: center; page-break-inside: avoid; } .figure img { max-width: 100%; height: auto; border: 1px solid #ddd; } .caption { font-size: 11pt; margin-top: 8px; font-weight: bold; } table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 11pt; } th { background-color: #f0f0f0; border: 1px solid #000; padding: 10px; font-weight: bold; text-align: left; } td { border: 1px solid #000; padding: 10px; } .reference-item { font-size: 11pt; margin-bottom: 10px; text-indent: -30px; padding-left: 30px; } /* SCREEN PREVIEW */ @media screen { body { background: #e0e0e0; display: flex; justify-content: center; padding: 20px 0; } .page-container { background: white; width: 210mm; min-height: 297mm; padding: 25mm; box-shadow: 0 0 20px rgba(0,0,0,0.15); box-sizing: border-box; } } /* PRINT EXPORT */ @media print { @page { size: A4; margin: 25mm; } body { background: none; display: block; padding: 0; } .page-container { width: 100%; min-height: auto; margin: 0; padding: 0; box-shadow: none; page-break-after: always; } .page-container:last-child { page-break-after: auto; } .cover-page, .certificate-title, .section-title, .chapter-title { page-break-after: avoid; } .figure, .table-container { page-break-inside: avoid; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }",
    "html": "<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body><div class='page-container'><div class='cover-page'><div><div class='college-logo'>{{logo}}</div><div class='college-name'>{{college_name}}</div><div class='department-name'>{{department}}</div></div><div><div class='report-label'>A Project Report on</div><div class='project-title'>{{title}}</div><div style='margin-top:20px;font-size:11pt;'>Submitted by</div><div class='student-info'>{{students}}</div><div class='guide-section'><div>Under the Guidance of</div><div class='guide-name'>{{guide_name}}</div><div>{{guide_designation}}</div></div></div><div class='submission-details'><div>In partial fulfillment of the requirements for the award of</div><div style='font-weight:bold;margin:10px 0;'>{{degree}}</div><div>in</div><div style='font-weight:bold;margin:10px 0;'>{{department}}</div><div class='academic-year'>{{academic_year}}</div></div></div></div><div class='page-container'><div class='certificate-title'>Certificate</div><div class='certificate-content'>{{certificate_content}}</div><div class='signature-section'><div style='text-align:center;'><div class='signature-line'></div><div><strong>Project Guide</strong></div><div>{{guide_name}}</div></div><div style='text-align:center;'><div class='signature-line'></div><div><strong>Head of Department</strong></div><div>{{hod_name}}</div></div></div></div><div class='page-container'><div class='section-title'>Acknowledgement</div><div style='margin-top:30px;'>{{acknowledgement}}</div></div><div class='page-container'><div class='section-title'>Table of Contents</div><div style='margin-top:30px;'>{{toc}}</div></div><div class='page-container'><div class='section-title'>Abstract</div><div style='margin-top:30px;'>{{abstract}}</div></div><div class='page-container'><div class='main-content'>{{content}}</div></div><div class='page-container'><div class='section-title'>References</div><div style='margin-top:30px;'>{{references}}</div></div></body></html>"
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
    "name": "IEEE Research Paper",
    "description": "Professional IEEE format with two-column layout, proper heading hierarchy, and academic styling. Ideal for research papers and technical documents.",
    "css": "/* SHARED */ * { margin: 0; padding: 0; box-sizing: border-box; } body { font-family: 'Times New Roman', Times, serif; font-size: 10pt; line-height: 1.5; color: #000; } h1 { font-size: 24pt; text-align: center; margin-bottom: 12pt; font-weight: bold; line-height: 1.2; } .byline { text-align: center; margin-bottom: 8pt; font-size: 10pt; } .author { margin-bottom: 4pt; } .affiliation { font-style: italic; margin-bottom: 2pt; } .email { margin-bottom: 8pt; } .abstract { margin: 12pt 0; text-align: justify; } .abstract-label { font-style: italic; font-weight: bold; } .abstract-text { font-weight: bold; display: inline; } .keywords { margin: 8pt 0 12pt 0; text-align: justify; } .keywords-label { font-style: italic; font-weight: bold; } .keywords-text { font-style: italic; display: inline; } .two-column { column-count: 2; column-gap: 0.25in; text-align: justify; margin-top: 12pt; } .heading-1 { text-align: center; font-variant: small-caps; margin-top: 12pt; margin-bottom: 6pt; font-weight: normal; font-size: 10pt; page-break-after: avoid; } .heading-2 { text-align: left; font-style: italic; margin-top: 10pt; margin-bottom: 6pt; font-weight: normal; font-size: 10pt; page-break-after: avoid; } .heading-3 { text-indent: 0.25in; font-style: italic; margin-top: 8pt; display: inline; font-weight: normal; font-size: 10pt; } .heading-3-content { display: inline; } .heading-4 { text-indent: 0.35in; font-style: italic; margin-top: 8pt; display: inline; font-weight: normal; font-size: 10pt; } .heading-4-content { display: inline; } .component-heading { text-align: center; font-variant: small-caps; margin-top: 12pt; margin-bottom: 6pt; font-weight: normal; font-size: 10pt; } p { margin-bottom: 6pt; text-indent: 0.25in; text-align: justify; } p.no-indent { text-indent: 0; } .figure, .table { margin: 12pt auto; text-align: center; page-break-inside: avoid; } .figure-caption, .table-caption { font-size: 9pt; margin-top: 6pt; text-align: center; } .figure img { max-width: 100%; height: auto; } .equation { text-align: center; margin: 10pt 0; page-break-inside: avoid; } .references { font-size: 9pt; } .reference-item { margin-bottom: 4pt; text-indent: -0.25in; padding-left: 0.25in; } table { margin: 6pt auto; border-collapse: collapse; border-top: 2px solid #000; border-bottom: 2px solid #000; } th { padding: 4pt 8pt; border-bottom: 1px solid #000; } td { padding: 4pt 8pt; } /* SCREEN PREVIEW */ @media screen { body { background: #e0e0e0; display: flex; justify-content: center; padding: 20px 0; } .page-container { background: white; width: 8.5in; min-height: 11in; padding: 0.75in 0.625in; box-shadow: 0 0 15px rgba(0,0,0,0.2); } } /* PRINT EXPORT */ @media print { @page { size: letter; margin: 0.75in 0.625in; } body { background: none; display: block; padding: 0; } .page-container { width: 100%; min-height: auto; padding: 0; box-shadow: none; page-break-after: always; } .page-container:last-child { page-break-after: auto; } h1, .heading-1, .heading-2, .component-heading { page-break-after: avoid; } .figure, .table, .equation { page-break-inside: avoid; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }",
    "html": "<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body><div class='page-container'><h1>{{title}}</h1><div class='byline'><div class='author'>{{author}}</div><div class='affiliation'>{{affiliation}}</div><div class='email'>{{email}}</div></div><div class='abstract'><span class='abstract-label'>Abstract—</span><span class='abstract-text'>{{abstract}}</span></div><div class='keywords'><span class='keywords-label'>Keywords—</span><span class='keywords-text'>{{keywords}}</span></div><div class='two-column'><div class='main-content'>{{content}}</div></div></div></body></html>"
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
    def __init__(self, model_name: str ="gemini-embedding-001"):
        self.model_name = model_name
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY")) # type: ignore


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

import sqlite3
import sqlite_vec
from typing import Optional, Tuple, Dict
# Assuming serialize_float32 is imported from your utils

class StyleRetriever:
    def __init__(self):
        self.embedder = GeminiEmbedding()
        
        # Initialize in-memory SQLite DB
        self.db = sqlite3.connect(":memory:") 
        self.db.enable_load_extension(True)
        sqlite_vec.load(self.db)
        self.db.enable_load_extension(False)
        
        # 1. Create Virtual Table
        # We replace +css and +html with metadata for the new engine
        self.db.execute("""
            CREATE VIRTUAL TABLE styles USING vec0(
                id INTEGER PRIMARY KEY,
                embedding float[3072],
                name TEXT,
                description TEXT,
                +preview_class TEXT,      -- Tailwind class for React Canvas
                +tex_template_path TEXT,  -- Path to the .tex file on disk
                +export_engine TEXT       -- 'xelatex' or 'pdflatex'
            )
        """)
        
        # 2. Populate DB
        self._populate_initial_data()

    def _populate_initial_data(self):
        print("Populating database with modern styles...")
        
        descriptions = [f"{t['name']}. {t['description']}" for t in MODERN_STYLE_TEMPLATES]
        embeddings = self.embedder.embed_documents(descriptions)

        for i, template in enumerate(MODERN_STYLE_TEMPLATES):
            vector = embeddings[i]
            
            # Note: We extract export_config details to the flat SQLite columns
            self.db.execute(
                """INSERT INTO styles(
                    id, embedding, name, description, 
                    preview_class, tex_template_path, export_engine
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    template["id"],
                    serialize_float32(vector),
                    template["name"],
                    template["description"],
                    template["preview_class"],
                    template["export_config"].get("template", "default.tex"),
                    template["export_config"].get("engine", "xelatex")
                )
            )
        print(f"Successfully populated {len(MODERN_STYLE_TEMPLATES)} styles.")

    def search_style(self, user_query: str) -> Dict:
        """
        Performs vector search and returns the full theme configuration.
        """
        # 1. Embed user query
        query_vector = self.embedder.embed_query(user_query)
        
        # 2. Perform Vector Search to get the ID/Name
        cursor = self.db.execute("""
            SELECT id, name, preview_class, tex_template_path, export_engine, distance
            FROM styles
            WHERE embedding MATCH ?
            AND k = 1
            ORDER BY distance
        """, (serialize_float32(query_vector),))
        
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "preview_class": row[2],
                "tex_template_path": row[3],
                "export_engine": row[4],
                "distance": row[5]
            }
        return {}


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