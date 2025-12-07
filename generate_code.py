import google.generativeai as genai
import os
import json
import base64
MEMORY_FILE = "memory.json"
def get_memory_string():
    if not os.path.exists(MEMORY_FILE): return ""
    with open(MEMORY_FILE, "r") as f: rules = json.load(f)
    return "\n\n**LEARNED USER RULES:**\n" + "\n".join([f"- {r}" for r in rules]) if rules else ""

def generate_standard_code(prompt, style_json, contexts, logo_file, image_refs, api_key):
    """
    Generates HTML that strictly clones the reference layout while applying
    specific style rules and user content.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # 1. Prepare Contexts
    clean_contexts = [ctx if ctx.strip() else "Unknown Component" for ctx in contexts]
    context_str = "\n".join([f"- Image {i+1}: {ctx}" for i, ctx in enumerate(clean_contexts)])
    print("CONTEXT STR:", context_str)
    print("Style JSON:", style_json)
    print("Image Refs:", image_refs)
    print("Prompt:", prompt)
    print("User rules:", get_memory_string())
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
    if image_refs:
        payload.extend(image_refs)
    
    # 4. Generate
    response = model.generate_content(payload)
    raw_html = response.text.replace("```html", "").replace("```", "")
    
    # 5. Handle Logo Replacement
    if logo_file:
        b64 = image_to_base64(logo_file)
        raw_html = raw_html.replace("LOGO_TOKEN", b64)
    else:
        raw_html = raw_html.replace("LOGO_TOKEN", "https://via.placeholder.com/150x50?text=Logo")

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
            backgroundColor: null
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



# def generate_standard_code(prompt, style_json, contexts, logo_file, api_key):
#     """Standard generation logic."""
#     genai.configure(api_key=api_key)
#     # model = genai.GenerativeModel(get_model())
#     # model = genai.GenerativeModel("models/gemini-2.5-pro-latest")
#     print(genai.list_models())
#     model = genai.GenerativeModel('gemini-2.5-flash')
    
#     clean_contexts = [ctx if ctx.strip() else "Unknown Component" for ctx in contexts]
#     context_str = "\n".join([f"- Image {i+1}: {ctx}" for i, ctx in enumerate(clean_contexts)])
#     memory_str = get_memory_string()
    
#     system_prompt = f"""
#     You are a Senior Frontend Architect.
#     Task: Write a COMPLETE HTML/TailwindCSS prototype for: "{prompt}"
    
#     CONTEXT: {context_str}
#     DESIGN SYSTEM: {style_json}
#     MEMORY: {memory_str}
    
#     LOGO INSTRUCTION: If logo needed, use src="LOGO_TOKEN"
    
#     DESIGN MODE: Add the 'Design Mode' script (draggable/editable) at the bottom.
    
#     OUTPUT: Return ONLY valid HTML code.
#     """
    
#     response = model.generate_content(system_prompt)
#     raw_html = response.text.replace("```html", "").replace("```", "")

#     download_script = """
#     <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
#     <script>
#     function downloadAsImage() {
#         const element = document.body;
#         html2canvas(element, {
#             useCORS: true, # Important for external images/logos
#             allowTaint: true,
#             backgroundColor: null
#         }).then(canvas => {
#             const link = document.createElement('a');
#             link.download = 'marketing-asset.png';
#             link.href = canvas.toDataURL();
#             link.click();
#         });
#     }
#     </script>
#     <div style="position: absolute; top: 10px; right: 10px; z-index: 1000;">
#         <button onclick="downloadAsImage()" style="background: #222; color: #fff; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer;">
#             📸 Download as Image
#         </button>
#     </div>
#     """
#     # When returning the code in generate_standard_code:
#     raw_html = raw_html.replace("</body>", f"{download_script}</body>")
    
#     if logo_file:
#         b64 = image_to_base64(logo_file)
#         return raw_html.replace("LOGO_TOKEN", b64)
#     else:
#         return raw_html.replace("LOGO_TOKEN", "https://via.placeholder.com/150x50?text=Logo")


# def generate_standard_code(prompt, style_json, contexts, logo_file, api_key):
#     """
#     Generates Marketing Assets (Banners/Posters) instead of full Apps.
#     Includes 'Download as Image' functionality automatically.
#     """
#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel(get_model())
    
#     # 1. Prepare Contexts
#     clean_contexts = [ctx if ctx.strip() else "Unknown Component" for ctx in contexts]
#     context_str = "\n".join([f"- Image {i+1}: {ctx}" for i, ctx in enumerate(clean_contexts)])
#     memory_str = get_memory_string()
    
#     # 2. NEW SYSTEM PROMPT (Marketing Asset Generator)
#     system_prompt = f"""
#     You are a Corporate Brand Designer.
#     Task: Create a MARKETING BANNER (HTML/TailwindCSS) for: "{prompt}"
    
#     CONTEXT & ASSETS:
#     {context_str}
    
#     STYLE GUIDES:
#     - Colors & Fonts: Extract rules from {style_json}
#     - Layout: Single screen, centered content, hero section style. 
#     - Dimensions: Optimize for 1200x630px (Social Media Card size), but make it responsive.
#     - Typography: Large, bold, impactful.
    
#     USER MEMORY/RULES:
#     {memory_str}
    
#     CONTENT RULES:
#     - Logo: Use src="LOGO_TOKEN" where appropriate.
#     - Headline: Create a catchy headline based on the user request.
#     - Call to Action: Use high-contrast buttons.
    
#     OUTPUT: Return ONLY valid HTML code with TailwindCSS classes. Do not include markdown code blocks.
#     """
    
#     # 3. Generate Content
#     response = model.generate_content(system_prompt)
#     raw_html = response.text.replace("```html", "").replace("```", "")
    
#     # 4. Handle Logo Replacement
#     if logo_file:
#         b64 = image_to_base64(logo_file)
#         raw_html = raw_html.replace("LOGO_TOKEN", b64)
#     else:
#         raw_html = raw_html.replace("LOGO_TOKEN", "https://via.placeholder.com/150x50?text=Logo")

#     # 5. Inject 'Download as Image' Script
#     download_script = """
#     <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
#     <div style="position: absolute; top: 10px; right: 10px; z-index: 9999;">
#         <button onclick="downloadAsImage()" style="background: #222; color: #fff; padding: 10px 15px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
#             📸 Download as Image
#         </button>
#     </div>
#     <script>
#     function downloadAsImage() {
#         const element = document.body;
#         html2canvas(element, {
#             useCORS: true,
#             allowTaint: true,
#             backgroundColor: null
#         }).then(canvas => {
#             const link = document.createElement('a');
#             link.download = 'marketing_asset_' + new Date().getTime() + '.png';
#             link.href = canvas.toDataURL();
#             link.click();
#         });
#     }
#     </script>
#     """
    
#     # Append script before closing body tag or at end of file
#     if "</body>" in raw_html:
#         final_html = raw_html.replace("</body>", f"{download_script}</body>")
#     else:
#         final_html = raw_html + download_script
        
#     return final_html

# def generate_standard_code(prompt, style_json, contexts, logo_file, image_refs, api_key):
#     """
#     Updated: Accepts 'image_refs' (Gemini File Objects) to keep visual context 
#     during code generation.
#     """
#     genai.configure(api_key=api_key)
#     # model = genai.GenerativeModel(get_model())
#     model = genai.GenerativeModel('gemini-2.5-flash')

    
#     # 1. Prepare Contexts
#     clean_contexts = [ctx if ctx.strip() else "Unknown Component" for ctx in contexts]
#     context_str = "\n".join([f"- Image {i+1}: {ctx}" for i, ctx in enumerate(clean_contexts)])
#     memory_str = get_memory_string()
    
#     # 2. SYSTEM PROMPT (Marketing Asset Generator)
#     system_prompt = f"""
#     You are a Corporate Brand Designer for the company, you will be given templates and instructions and you will have to create new templates using the old ones and the instructions given. Use same branding and theme from the reference templates / images.
#     Task: Create a MARKETING BANNER (HTML/TailwindCSS) for: "{prompt}"
    
#     VISUAL REFERENCES:
#     I have attached the source design files. Use them to ensure the output looks exactly like the brand style.
    
#     CONTEXT & ASSETS:
#     {context_str}
    
#     STYLE GUIDES (Extracted):
#     - Colors & Fonts: Extract rules from {style_json}
#     - Layout: Single screen, centered content, hero section style. 
#     - Dimensions: Optimize for 1200x630px (Social Media Card size), but make it responsive.
#     - Typography: Large, bold, impactful.
    
#     USER MEMORY/RULES:
#     {memory_str}
    
#     CONTENT RULES:
#     - Logo: Use src="LOGO_TOKEN" where appropriate.
#     - Headline: Create a catchy headline based on the user request.
#     - Call to Action: Use high-contrast buttons.
    
#     OUTPUT: Return ONLY valid HTML code with TailwindCSS classes. Do not include markdown code blocks.
#     """
    
#     # 3. Construct Payload: Prompt + Original File Objects
#     # This allows Gemini to "look" at the high-res files again while coding
#     print("Preparing payload with visual references...", system_prompt, image_refs)
#     payload = [system_prompt]
#     if image_refs:
#         payload.extend(image_refs)
    
#     # 4. Generate
#     response = model.generate_content(payload)
#     raw_html = response.text.replace("```html", "").replace("```", "")
    
#     # 5. Handle Logo Replacement
#     if logo_file:
#         b64 = image_to_base64(logo_file)
#         raw_html = raw_html.replace("LOGO_TOKEN", b64)
#     else:
#         raw_html = raw_html.replace("LOGO_TOKEN", "https://via.placeholder.com/150x50?text=Logo")

#     # 6. Inject 'Download as Image' Script
#     download_script = """
#     <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
#     <div style="position: absolute; top: 10px; right: 10px; z-index: 9999;">
#         <button onclick="downloadAsImage()" style="background: #222; color: #fff; padding: 10px 15px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
#             📸 Download as Image
#         </button>
#     </div>
#     <script>
#     function downloadAsImage() {
#         const element = document.body;
#         html2canvas(element, {
#             useCORS: true,
#             allowTaint: true,
#             backgroundColor: null
#         }).then(canvas => {
#             const link = document.createElement('a');
#             link.download = 'marketing_asset_' + new Date().getTime() + '.png';
#             link.href = canvas.toDataURL();
#             link.click();
#         });
#     }
#     </script>
#     """
    
#     if "</body>" in raw_html:
#         final_html = raw_html.replace("</body>", f"{download_script}</body>")
#     else:
#         final_html = raw_html + download_script
        
#     return final_html
