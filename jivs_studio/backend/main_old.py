import logging
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI, APIError, RateLimitError, AuthenticationError, BadRequestError
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
import io
import base64
import os
import requests

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.critical("OPENAI_API_KEY is missing.")
    raise RuntimeError("OPENAI_API_KEY is not set.")

client = OpenAI(api_key=api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- UTILS ---
def decode_base64_image(b64_string: str):
    try:
        if "base64," in b64_string:
            b64_string = b64_string.split("base64,")[1]
        image_data = base64.b64decode(b64_string)
        return Image.open(io.BytesIO(image_data))
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        raise HTTPException(status_code=400, detail="Invalid image data.")

# --- ENDPOINTS ---

@app.post("/generate")
async def generate_design(
    prompt: str = Form(...),
    files: list[UploadFile] = File(default=[])
):
    """Step 1: Analyzes uploaded assets and generates the initial UI."""
    try:
        # 1. Vision Analysis (GPT-4o-mini)
        messages_content = [
            {"type": "text", "text": (
                "You are an Expert UI/UX Designer. Analyze the user request and reference images. "
                "Generate a detailed image generation prompt for a modern UI design. "
                "Return ONLY the prompt string."
            )}
        ]
        messages_content.append({"type": "text", "text": f"User Prompt: {prompt}"})

        for file in files:
            content = await file.read()
            if len(content) > 0:
                b64_img = base64.b64encode(content).decode("utf-8")
                messages_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64_img}"}
                })

        logger.info("Generating prompt with Vision...")
        vision_res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": messages_content}],
            max_tokens=300
        )
        final_prompt = vision_res.choices[0].message.content
        logger.info(f"Generated Prompt: {final_prompt[:50]}...")

        # 2. Image Generation
        # FIX: Removed 'response_format' parameter
        logger.info("Calling Image Model...")
        img_res = client.images.generate(
            model="dall-e-3", # Recommended: Switch to dall-e-3 for best stability if gpt-image-1 fails
            prompt=final_prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json" # DALL-E 3 SUPPORTS this. gpt-image-1 DOES NOT.
        )
        
        # If you MUST use gpt-image-1, use this block instead:
        """
        img_res = client.images.generate(
            model="gpt-image-1-mini",
            prompt=final_prompt,
            n=1,
            size="1024x1024"
            # NO response_format line here
        )
        """

        # Handle output (DALL-E 3 returns b64_json if requested)
        if hasattr(img_res.data[0], 'b64_json') and img_res.data[0].b64_json:
            image_data = img_res.data[0].b64_json
            return {"image": f"data:image/png;base64,{image_data}"}
        
        # Fallback if model returns a URL (common default for some models)
        elif hasattr(img_res.data[0], 'url') and img_res.data[0].url:
            image_url = img_res.data[0].url
            # Download the image to convert to base64 for frontend
            response = requests.get(image_url)
            b64_downloaded = base64.b64encode(response.content).decode('utf-8')
            return {"image": f"data:image/png;base64,{b64_downloaded}"}

    except Exception as e:
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=str(e))

class RefineRequest(BaseModel):
    original_image: str
    annotation_overlay: str
    instructions: str

@app.post("/refine")
async def refine_design(req: RefineRequest):
    """Step 2: Refinement"""
    try:
        # 1. Vision Analysis
        messages_content = [
            {"type": "text", "text": (
                f"The user wants to edit a UI. Instructions: '{req.instructions}'. "
                f"Image 1 is the original. Image 2 contains red box annotations of changes. "
                f"Write a NEW detailed image prompt to generate the result."
            )},
            {"type": "image_url", "image_url": {"url": req.original_image}},
            {"type": "image_url", "image_url": {"url": req.annotation_overlay}}
        ]

        logger.info("Analyzing refinement...")
        vision_res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": messages_content}],
            max_tokens=300
        )
        new_prompt = vision_res.choices[0].message.content

        # 2. Re-Generation
        logger.info("Regenerating...")
        img_res = client.images.generate(
            model="dall-e-3", # Switched to DALL-E 3 for safety
            prompt=new_prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json"
        )

        return {"image": f"data:image/png;base64,{img_res.data[0].b64_json}"}

    except Exception as e:
        logger.exception("Refinement failed")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)