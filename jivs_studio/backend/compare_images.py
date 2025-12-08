import google.generativeai as genai
import json
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

def compare_images_gemini(original_image: Image.Image, generated_image: Image.Image, api_key: str):
    """
    Compares two PIL images using Gemini 1.5 Pro and returns a similarity score + feedback.
    """
    genai.configure(api_key=api_key)
    
    # Use Pro for better vision analysis
    model = genai.GenerativeModel(
        'gemini-2.5-flash-lite',
        generation_config={"response_mime_type": "application/json"}
    )

    system_prompt = """
    You are a QA Design Engineer. 
    Analyze these two UI screenshots. 
    Image 1 is the ORIGINAL DESIGN REFERENCE.
    Image 2 is the GENERATED FRONTEND CODE OUTPUT.

    Your task is to compare them based *strictly* on visual accuracy.

    1. Compare specific elements:
       - Layout & Alignment
       - Colors & Backgrounds
       - Typography (Fonts, Sizes, Weights)
       - Spacing & Padding
       - Component Styling (Rounded corners, shadows)
    
    2. Determine a "similarity_score" from 0 to 100.
       - 100 = Pixel Perfect match.
       - 50-99 = Minor visual differences (e.g., slightly different font).
       - < 50 = Major layout or styling issues.

    3. List "dissimilar_features": specific actionable feedback on what is wrong in Image 2.

    Output JSON structure:
    {
        "similarity_score": <integer>,
        "similar_features": ["feature 1", ...],
        "dissimilar_features": ["The button color is blue instead of red", "The logo is on the wrong side", ...]
    }
    """

    prompt = "Compare these two images. Provide the JSON analysis."

    try:
        # Gemini accepts PIL images directly in the list
        response = model.generate_content([system_prompt, original_image, generated_image, prompt])
        
        # Parse JSON
        result = json.loads(response.text)
        return result

    except Exception as e:
        logger.error(f"Comparison Error: {e}")
        # Return a fallback in case of error
        return {
            "similarity_score": 0,
            "similar_features": [],
            "dissimilar_features": [f"Error during comparison: {str(e)}"]
        }