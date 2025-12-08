import logging
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import base64
import os
import io
import json
from PIL import Image
import google.generativeai as genai
from vector_store import DesignMemory

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

# --- CONFIGURATION ---
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_KEY:
    logger.warning("GOOGLE_API_KEY is missing. Please add it to your .env file.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- UTILS ---
def image_to_base64(image_file):
    """Converts a file-like object or PIL Image to base64 string"""
    try:
        # If it's a PIL Image, save to buffer first
        if isinstance(image_file, Image.Image):
            buffered = io.BytesIO()
            image_file.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # If it's a raw UploadFile/BytesIO
        image_file.seek(0)
        return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Base64 conversion error: {e}")
        return ""

def get_memory_string():
    """Retrieves learned user rules (Placeholder for your memory logic)"""
    memory_file = "memory.json"
    if os.path.exists(memory_file):
        try:
            with open(memory_file, "r") as f:
                rules = json.load(f)
            return "\n\n**LEARNED USER RULES:**\n" + "\n".join([f"- {r}" for r in rules]) if rules else ""
        except:
            return ""
    return ""

# --- THE CORE FUNCTION (As Requested) ---
def generate_standard_code(prompt, style_json, contexts, logo_file, image_refs, api_key):
    """
    Generates HTML that strictly clones the reference layout while applying
    specific style rules and user content.
    """
    genai.configure(api_key=api_key)
    # Note: Ensure your API key has access to 'gemini-2.5-flash' (or use 'gemini-1.5-flash')
    try:
        model = genai.GenerativeModel("gemini-1.5-flash") # Fallback to 1.5 if 2.5 is not public yet
    except:
        model = genai.GenerativeModel("gemini-1.5-pro")

    # 1. Prepare Contexts
    clean_contexts = [ctx if ctx.strip() else "Unknown Component" for ctx in contexts]
    context_str = "\n".join([f"- Image {i+1}: {ctx}" for i, ctx in enumerate(clean_contexts)])
    
    print("CONTEXT STR:", context_str)
    # print("Style JSON:", style_json) # Commented out for cleaner logs
    print("Prompt:", prompt)
    
    memory_str = get_memory_string()
    
    # 2. SYSTEM PROMPT (Strict Layout Cloner)
    system_prompt = f"""
    You are a Frontend Cloning Expert specialized in pixel-perfect HTML/TailwindCSS replication.
    
    **YOUR MISSION:**
    1. **CLONE THE LAYOUT:** Look at the attached 'VISUAL REFERENCES'. Your HTML structure (grid, spacing, alignment, element placement) must mimic the reference image EXACTLY. Do not invent a generic "hero section" or "marketing template" unless no image is provided.
    2. **APPLY THE BRANDING:** Use the colors, border-radii, and shadows defined in 'STYLE GUIDES'.
    3. **INJECT CONTENT:** Use the 'USER INSTRUCTION' to determine what the text should say.
    
    **INPUTS:**
    - USER INSTRUCTION: "{prompt}"
    - USER RULES: {memory_str}
    
    **CONTENT RULES (CRITICAL):**
    1. **Specific Text:** If the 'USER INSTRUCTION' provides a headline or specific copy, use it.
    2. **Filler Text:** For all other text areas visible in the reference layout (body paragraphs, secondary cards, nav links) where the user did NOT provide specific text, use **Lorem Ipsum**. Do NOT invent "marketing fluff" or generic English copy. Use Lorem Ipsum to preserve the visual density of the design.
    3. **Images:** - Use `src="LOGO_TOKEN"` for the primary logo.
       - Use `https://via.placeholder.com/WIDTHxHEIGHT` for all other images seen in the layout.
    
    **OUTPUT:** Return ONLY valid HTML code with TailwindCSS classes. Do not include markdown code blocks.
    """
    
    # 3. Construct Payload: Prompt + Original File Objects
    # Passing image_refs allows Gemini to "see" the layout grid
    payload = [system_prompt]
    
    # Gemini Python SDK expects PIL images in the list
    if image_refs:
        payload.extend(image_refs)
    
    # 4. Generate
    logger.info("Sending payload to Gemini...")
    response = model.generate_content(payload)
    raw_html = response.text.replace("```html", "").replace("```", "")
    
    # 5. Handle Logo Replacement
    if logo_file:
        b64 = image_to_base64(logo_file)
        raw_html = raw_html.replace("LOGO_TOKEN", f"data:image/png;base64,{b64}")
    else:
        # Use a better placeholder service
        raw_html = raw_html.replace("LOGO_TOKEN", "https://placehold.co/150x50?text=Logo")

    # 6. Inject 'Download as Image' Script
    download_script = """
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <div style="position: absolute; top: 10px; right: 10px; z-index: 9999;">
        <button onclick="downloadAsImage()" style="background: #222; color: #fff; padding: 10px 15px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            📸 Download as Image
        </button>
    </div>
    <script>
    function downloadAsImage() {
        const element = document.body;
        html2canvas(element, {
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff', // Ensure white bg
            scale: 2 // High res
        }).then(canvas => {
            const link = document.createElement('a');
            link.download = 'marketing_asset_' + new Date().getTime() + '.png';
            link.href = canvas.toDataURL();
            link.click();
        });
    }
    </script>
    """
    
    if "</body>" in raw_html:
        final_html = raw_html.replace("</body>", f"{download_script}</body>")
    else:
        final_html = raw_html + download_script
        
    return final_html


# --- ADD THIS TO backend/main.py (Before the @app.post endpoints) ---

SYSTEM_PROMPT = """
You are an Expert Frontend Developer. 
Your task is to convert UI screenshots into production-ready HTML using Tailwind CSS.

1. Output ONLY the raw HTML code (no markdown, no ```html``` blocks).
2. Use valid Tailwind CSS classes for all styling (colors, layout, spacing, typography).
3. Do NOT include <html>, <head>, or <body> tags. Output only the content inside the body (e.g., <div class="...">...</div>).
4. Use placeholder images (e.g., https://placehold.co/600x400) where necessary.
5. Ensure the design is responsive and matches the visual hierarchy of the input image.
"""
# Initialize Memory
design_memory = DesignMemory()

# --- ENDPOINTS ---


@app.post("/generate-code")
async def generate_code(
    prompt: str = Form(...),
    files: list[UploadFile] = File(default=[])
):
    try:
        # 1. SEARCH MEMORY: Does the user want a specific style?
        # We query Qdrant with the user's prompt (e.g., "Make a dashboard like S/4")
        retrieved_style = design_memory.find_similar_style(prompt)
        
        style_context = ""
        if retrieved_style and retrieved_style.metadata:
             print(f"🎯 Found relevant style: {retrieved_style.metadata['name']}")
             style_context = f"""
             **STRICT VISUAL STYLE GUIDE (FROM DATABASE):**
             - Base Design: {retrieved_style.metadata['name']}
             - Style Rules: {retrieved_style.metadata.get('style_rules', 'N/A')}
             - Reference Image Path: {retrieved_style.metadata.get('image_path')}
             
             PLEASE ADHERE TO THIS VISUAL THEME.
             """

        # 2. PREPARE PROMPT
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": []}
        ]
        
        # Combine User Prompt + Retrieved Style Context
        full_instruction = f"User Request: {prompt}\n\n{style_context}"
        
        messages[1]["content"].append({"type": "text", "text": full_instruction})

        # Add Images (if any uploaded)
        for file in files:
            content = await file.read()
            if len(content) > 0:
                b64 = base64.b64encode(content).decode("utf-8")
                messages[1]["content"].append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                })

        # 3. GENERATE
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            max_tokens=4000
        )
        
        code = response.choices[0].message.content.replace("```html", "").replace("```", "")
        return {"html": code}

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""
@app.post("/generate-code")
async def generate_code_endpoint(
    prompt: str = Form(...),
    files: list[UploadFile] = File(default=[])
):
    """
"""Endpoint that receives the frontend request and calls your custom generator function."""
"""
    if not GOOGLE_KEY:
        raise HTTPException(status_code=500, detail="Server Configuration Error: GOOGLE_API_KEY missing.")

    try:
        # 1. Process Images for Gemini
        # We need to convert FastAPI UploadFiles into PIL Images
        pil_images = []
        logo_image = None
        
        for file in files:
            content = await file.read()
            image = Image.open(io.BytesIO(content))
            
            # Simple logic: If user names file 'logo', treat as logo, otherwise ref
            # For now, let's assume all uploads are references unless specific logic exists
            pil_images.append(image)

        # 2. Call your logic
        # We pass empty style/contexts for now as the React app sends raw files
        final_html = generate_standard_code(
            prompt=prompt,
            style_json="{}", 
            contexts=[], 
            logo_file=logo_image, # Pass None for now, or extract from files if you implement logic
            image_refs=pil_images,
            api_key=GOOGLE_KEY
        )
        
        return {"html": final_html}

    except Exception as e:
        logger.error(f"Generate Code Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class RefineCodeRequest(BaseModel):
    current_html: str
    instructions: str
"""
@app.post("/refine-code")
async def refine_code_endpoint(req: RefineCodeRequest):
    """
    Refines existing HTML using Gemini (Text-to-Text mode).
    """
    genai.configure(api_key=GOOGLE_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        logger.info("Refining code with Gemini...")
        
        prompt = f"""
        You are an Expert Frontend Developer.
        
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