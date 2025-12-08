import logging
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import base64
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PROMPTS ---
SYSTEM_PROMPT = """
You are an Expert Frontend Developer. 
Your task is to convert UI screenshots into production-ready HTML using Tailwind CSS.
1. Output ONLY the raw HTML code (no markdown, no ```html``` blocks).
2. Use valid Tailwind CSS classes for all styling (colors, layout, spacing, typography).
3. Do NOT include <html>, <head>, or <body> tags. Output only the content inside the body (e.g., <div class="...">...</div>).
4. Use placeholder images (e.g., https://placehold.co/600x400) where necessary.
5. Ensure the design is responsive and matches the visual hierarchy of the input image.
"""

@app.post("/generate-code")
async def generate_code(
    prompt: str = Form(...),
    files: list[UploadFile] = File(default=[])
):
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": []}
        ]
        
        # Add User Prompt
        messages[1]["content"].append({"type": "text", "text": f"Build this UI. Context: {prompt}"})

        # Add Images
        for file in files:
            content = await file.read()
            if len(content) > 0:
                b64 = base64.b64encode(content).decode("utf-8")
                messages[1]["content"].append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                })

        logger.info("Generating code with GPT-4o...")
        response = client.chat.completions.create(
            model="gpt-4o", # GPT-4o is best for code generation
            messages=messages,
            max_tokens=4000,
            temperature=0.2
        )
        
        code = response.choices[0].message.content.replace("```html", "").replace("```", "")
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
        logger.info("Refining code...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Current HTML:\n{req.current_html}\n\nUser Instructions: {req.instructions}\n\nOutput the fully updated HTML code."}
            ]
        )
        code = response.choices[0].message.content.replace("```html", "").replace("```", "")
        return {"html": code}
    except Exception as e:
        logger.error(f"Refine Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)