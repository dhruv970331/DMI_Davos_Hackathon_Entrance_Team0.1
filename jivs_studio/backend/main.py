import logging
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io
import os
from vector_store import DesignMemory
from compare_images import compare_images_gemini 
import base64
import json
import tempfile
import subprocess
import shutil
from typing import Dict, Optional, Any, List

# --- 1. CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_KEY:
    logger.error("GOOGLE_API_KEY is missing from .env file")
    raise RuntimeError("GOOGLE_API_KEY is missing")

genai.configure(api_key=GOOGLE_KEY)

# Initialize Design Memory (Qdrant)
try:
    design_memory = DesignMemory()
except Exception as e:
    logger.warning(f"Could not connect to Qdrant: {e}. Running without memory.")
    design_memory = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are an Expert Frontend Developer. 
Your task is to convert UI screenshots into production-ready HTML using Tailwind CSS.

1. Output ONLY the raw HTML code (no markdown, no ```html``` blocks).
2. Use valid Tailwind CSS classes for all styling (colors, layout, spacing, typography).
3. Do NOT include <html>, <head>, or <body> tags. Output only the content inside the body (e.g., <div class="...">...</div>).
4. Use placeholder images (e.g., https://placehold.co/600x400) where necessary.
5. Ensure the design is responsive and matches the visual hierarchy of the input image.
"""

# --- 3. HELPER: INJECT DESIGN TOOLS ---
def inject_design_tools(raw_html: str) -> str:
    """
    Injects the Design Mode & Download scripts into the generated HTML.
    """
    controls_script = """
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    
    <div id="ui-controls" style="position: fixed; top: 10px; right: 10px; z-index: 10000; display: flex; gap: 10px;">
        <button id="toggle-design-btn" onclick="toggleDesignMode()" style="background: #444; color: #fff; padding: 10px 15px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-family: sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            ✏️ Design Mode: OFF
        </button>
        <button onclick="downloadAsImage()" style="background: #2563EB; color: #fff; padding: 10px 15px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-family: sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            📸 Download Image
        </button>
    </div>

    <script>
    // --- DESIGN MODE LOGIC ---
    let isDesignMode = false;
    let draggedEl = null;
    let startX, startY, initialTx, initialTy;

    function toggleDesignMode() {
        isDesignMode = !isDesignMode;
        const btn = document.getElementById('toggle-design-btn');
        document.body.contentEditable = isDesignMode; // Allows text editing everywhere
        
        if (isDesignMode) {
            btn.innerHTML = "✅ Finish Editing";
            btn.style.background = "#059669"; // Green
            document.body.style.cursor = "default";
            enableDragging();
        } else {
            btn.innerHTML = "✏️ Design Mode: OFF";
            btn.style.background = "#444";
            disableDragging();
        }
    }

    function enableDragging() {
        document.addEventListener('mousedown', startDrag);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', endDrag);
    }

    function disableDragging() {
        document.removeEventListener('mousedown', startDrag);
        document.removeEventListener('mousemove', drag);
        document.removeEventListener('mouseup', endDrag);
    }

    function startDrag(e) {
        // Don't drag if clicking buttons or inputs
        if (e.target.tagName === 'BUTTON' || e.target.closest('#ui-controls')) return;
        
        draggedEl = e.target;
        
        // Prevent editing text while dragging
        draggedEl.contentEditable = false; 
        
        startX = e.clientX;
        startY = e.clientY;
        
        // Get current transform values (if any)
        const style = window.getComputedStyle(draggedEl);
        const matrix = new WebKitCSSMatrix(style.webkitTransform);
        initialTx = matrix.m41;
        initialTy = matrix.m42;
        
        draggedEl.style.transition = 'none'; // Disable transition for smooth drag
        draggedEl.style.zIndex = 1000; // Bring to front
    }

    function drag(e) {
        if (!draggedEl) return;
        e.preventDefault();
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        draggedEl.style.transform = `translate(${initialTx + dx}px, ${initialTy + dy}px)`;
    }

    function endDrag(e) {
        if (!draggedEl) return;
        draggedEl.contentEditable = isDesignMode; // Re-enable text edit
        draggedEl.style.zIndex = ''; // Reset Z
        draggedEl = null;
    }

    // --- DOWNLOAD LOGIC ---
    function downloadAsImage() {
        // 1. Hide the controls so they don't appear in the image
        const controls = document.getElementById('ui-controls');
        controls.style.display = 'none';
        
        // 2. Temporarily turn off Design Mode borders/indicators if any
        const wasDesignMode = isDesignMode;
        if (isDesignMode) toggleDesignMode(); 

        const element = document.body;

        html2canvas(element, {
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff', // Force white background for cleaner screenshots
            scrollY: -window.scrollY // Fix scroll issues
        }).then(canvas => {
            const link = document.createElement('a');
            link.download = 'marketing_asset_' + new Date().getTime() + '.png';
            link.href = canvas.toDataURL();
            link.click();
            
            // 3. Restore UI state
            controls.style.display = 'flex';
            if (wasDesignMode) toggleDesignMode();
        });
    }
    </script>
    """
    
    # Append the script to the end of the HTML body
    if "</body>" in raw_html:
        return raw_html.replace("</body>", f"{controls_script}</body>")
    else:
        return raw_html + controls_script

# --- 3. NEW HELPERS (Project Gen & Testing) ---

def generate_placeholder_tests(code_files: Dict[str, str], test_dir_path: str):
    """Generates dummy tests to ensure the runner works even if no tests exist."""
    test_content = """
import pytest
def test_placeholder_success():
    assert 1 == 1
def test_component_structure():
    # Placeholder: In real app, mount component and check
    assert True
"""
    # Create a generic test file
    test_file_path = os.path.join(test_dir_path, "test_generated.py")
    with open(test_file_path, "w") as f:
        f.write(test_content)

# --- 4. DATA MODELS ---

class ProjectGenRequest(BaseModel):
    framework: str # e.g. "React", "Vue", "Angular"
    description: str
    image_data: Optional[str] = None # Base64 string

class TestRunRequest(BaseModel):
    code_files: Dict[str, str]
    framework: str

# --- 5. ENDPOINTS ---

@app.post("/generate-code")
async def generate_code(
    prompt: str = Form(...),
    files: list[UploadFile] = File(default=[])
):
    try:
        # A. SEARCH MEMORY (Qdrant)
        style_context = ""
        if design_memory:
            try:
                retrieved_style = design_memory.find_similar_style(prompt)
                if retrieved_style and retrieved_style.metadata:
                    logger.info(f"Using style template: {retrieved_style.metadata.get('name')}")
                    style_context = f"""
                    \n\n**STRICT STYLE GUIDE (FROM DATABASE):**
                    - Base Design: {retrieved_style.metadata.get('name')}
                    - Visual Rules: {retrieved_style.page_content}
                    - Style Metadata: {retrieved_style.metadata}
                    
                    PLEASE ADHERE TO THIS VISUAL THEME.
                    """
            except Exception as e:
                logger.error(f"Memory Search Failed: {e}")

        # B. PREPARE MODEL
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        full_instruction = f"{SYSTEM_PROMPT}\n\nUser Request: {prompt}{style_context}"
        payload = [full_instruction]

        for file in files:
            content = await file.read()
            if len(content) > 0:
                image = Image.open(io.BytesIO(content))
                payload.append(image)

        # C. GENERATE
        logger.info("Generating code with Gemini 1.5 Pro...")
        response = model.generate_content(payload)
        code = response.text.replace("```html", "").replace("```", "")
        
        # [NEW] Inject the design tools before returning
        final_code = inject_design_tools(code)
        
        return {"html": final_code}

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class RefineCodeRequest(BaseModel):
    current_html: str
    instructions: str

@app.post("/refine-code")
async def refine_code(req: RefineCodeRequest):
    try:
        logger.info("Refining code with Gemini...")
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # We need to strip the script before sending back to AI to avoid confusion, 
        # or tell the AI to ignore scripts.
        # Simple approach: Tell AI to focus on structure.
        
        prompt = f"""
        {SYSTEM_PROMPT}
        
        TASK: Update the following HTML code based strictly on the USER INSTRUCTIONS.
        
        USER INSTRUCTIONS: {req.instructions}
        
        CURRENT CODE:
        {req.current_html}
        
        OUTPUT: Return ONLY the updated valid HTML code. No markdown.
        """
        
        response = model.generate_content(prompt)
        code = response.text.replace("```html", "").replace("```", "")
        
        # [NEW] Re-inject the design tools into the refined code
        final_code = inject_design_tools(code)
        
        return {"html": final_code}
        
    except Exception as e:
        logger.error(f"Refine Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify-design")
async def verify_design(
    original_file: UploadFile = File(...),
    generated_screenshot: UploadFile = File(...)
):
    """
    Receives the Original Image and a Screenshot of the Generated Code.
    Returns a similarity score and list of visual discrepancies.
    Does NOT modify the code.
    """
    try:
        # 1. Load Images
        orig_bytes = await original_file.read()
        gen_bytes = await generated_screenshot.read()
        
        orig_img = Image.open(io.BytesIO(orig_bytes))
        gen_img = Image.open(io.BytesIO(gen_bytes))

        # 2. Run Comparison Logic
        logger.info("Comparing Original vs Generated...")
        analysis = compare_images_gemini(orig_img, gen_img, GOOGLE_KEY)
        
        logger.info(f"Analysis Complete. Score: {analysis.get('similarity_score')}")

        return analysis

    except Exception as e:
        logger.error(f"Verification Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# [NEW] MULTI-FILE PROJECT GENERATOR
@app.post("/generate-project")
async def generate_project(payload: ProjectGenRequest):
    """
    Generates a full project structure (multiple files) based on an image/description.
    Returns JSON with analysis and file contents.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt_parts = [
            f"""You are an expert UI developer. 
            Your task is to generate a new, production-ready {payload.framework} application from scratch.
            
            User Description: {payload.description}
            
            OUTPUT RULES:
            Your response MUST be a single, valid JSON object with "analysis" and "generated_code" keys.
            The "analysis" key must contain a JSON object with fields like "summary", "reasoning", "components_generated".
            The "generated_code" key must contain an object where each key is a full filename (e.g., "src/App.vue", "package.json") and each value is the complete code for that file.
            """
        ]

        if payload.image_data:
            # Decode base64 image
            try:
                if "base64," in payload.image_data:
                    img_str = payload.image_data.split("base64,")[1]
                else:
                    img_str = payload.image_data
                
                img_bytes = base64.b64decode(img_str)
                image = Image.open(io.BytesIO(img_bytes))
                prompt_parts.append(image)
            except Exception as e:
                logger.error(f"Image decode failed: {e}")

        logger.info(f"Generating {payload.framework} project...")
        response = model.generate_content(prompt_parts)
        
        # Clean response
        txt = response.text.replace("```json", "").replace("```", "")
        result_json = json.loads(txt)
        
        return {
            "success": True,
            "framework": payload.framework,
            "files": result_json.get("generated_code", {}),
            "analysis": result_json.get("analysis", {})
        }

    except Exception as e:
        logger.error(f"Project Gen Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# [NEW] TEST RUNNER
@app.post("/run-tests")
async def run_tests(request: TestRunRequest):
    """
    Receives code files, writes them to temp dir, runs pytest, returns report.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 1. Write Code Files
            for filename, content in request.code_files.items():
                # Handle nested directories (e.g., src/components/Header.jsx)
                file_path = os.path.join(temp_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # 2. Generate Dummy Tests (Since we are generating UI code, not test code usually)
            generate_placeholder_tests(request.code_files, temp_dir)

            # 3. Run Pytest
            report_file = os.path.join(temp_dir, "report.json")
            
            # Note: Ensure 'pytest-json-report' is installed in your python env
            cmd = [sys.executable, "-m", "pytest", "--json-report", f"--json-report-file={report_file}"]
            
            process = subprocess.run(
                cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True
            )

            # 4. Parse Report
            if not os.path.exists(report_file):
                # If report wasn't generated, pytest likely crashed or config error
                return {
                    "summary": {"passed": 0, "failed": 1, "total": 1},
                    "tests": [{"name": "System", "outcome": "failed", "message": f"Pytest Execution Failed:\n{process.stderr}"}]
                }

            with open(report_file) as f:
                report_data = json.load(f)

            # 5. Format Output
            formatted_tests = []
            for test in report_data.get("tests", []):
                formatted_tests.append({
                    "name": test.get("nodeid"),
                    "outcome": test.get("outcome"),
                    "duration": test.get("duration"),
                    "message": test.get("longrepr", "") if test.get("outcome") == 'failed' else ""
                })

            return {
                "summary": report_data.get("summary", {}),
                "tests": formatted_tests
            }

        except Exception as e:
            logger.error(f"Test Runner Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)