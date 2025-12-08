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

# --- 1. CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

# [FIX] Initialize Google Client
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

 # 2. SYSTEM PROMPT (Strict Layout Cloner)
SYSTEM_PROMPT = f"""
    You are a Frontend Cloning Expert specialized in pixel-perfect HTML/TailwindCSS replication.
    
    **YOUR MISSION:**
    1. **CLONE THE LAYOUT:** Look at the attached 'VISUAL REFERENCES'. Your HTML structure (grid, spacing, alignment, element placement) must mimic the reference image EXACTLY. Do not invent a generic "hero section" or "marketing template" unless no image is provided.
    2. **APPLY THE BRANDING:** Use the colors, border-radii, and shadows defined in 'STYLE GUIDES'.
    3. **INJECT CONTENT:** Use the 'USER INSTRUCTION' to determine what the text should say.
   
    
    **CONTENT RULES (CRITICAL):**
    1. **Specific Text:** If the 'USER INSTRUCTION' provides a headline or specific copy, use it.
    2. **Filler Text:** For all other text areas visible in the reference layout (body paragraphs, secondary cards, nav links) where the user did NOT provide specific text, use **Lorem Ipsum**. Do NOT invent "marketing fluff" or generic English copy. Use Lorem Ipsum to preserve the visual density of the design.
    3. **Images:** - Use `src="LOGO_TOKEN"` for the primary logo.
       - Use `https://via.placeholder.com/WIDTHxHEIGHT` for all other images seen in the layout.
    
    **OUTPUT:** Return ONLY valid HTML code with TailwindCSS classes. Do not include markdown code blocks.
    """
# --- 3. ENDPOINTS ---

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
        # We use Gemini 1.5 Pro for best coding capability
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # C. PREPARE CONTENT PAYLOAD
        # Gemini expects a list containing [Text Prompts, PIL Images...]
        
        full_instruction = f"{SYSTEM_PROMPT}\n\nUser Request: {prompt}{style_context}"
        
        payload = [full_instruction]

        # Add Images (Convert to PIL)
        for file in files:
            content = await file.read()
            if len(content) > 0:
                image = Image.open(io.BytesIO(content))
                payload.append(image)

        # D. GENERATE
        logger.info("Generating code with Gemini 1.5 Pro...")
        response = model.generate_content(payload)
        
        # Cleanup markdown
        code = response.text.replace("```html", "").replace("```", "")
        return {"html": code}

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
        model = genai.GenerativeModel('gemini-2.5-flash')
        
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
        return {"html": code}
        
    except Exception as e:
        logger.error(f"Refine Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)