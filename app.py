import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os
import base64
import webbrowser
from datetime import datetime
from generate_code import (generate_standard_code)

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="JiVS Auto-Coder: Redesign Edition")

st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 6px; font-weight: 600; }
    h1 { color: #0066cc; }
    .stTextInput input { font-weight: bold; color: #2d3748; background-color: #f8f9fa; }
    .stHeader { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. ASSET MANAGER ---
class AssetManager:
    def __init__(self, root_dir="ji_project_assets"):
        self.root_dir = root_dir
        self.upload_dir = os.path.join(root_dir, "uploads")
        self.gen_dir = os.path.join(root_dir, "generated_code")
        self.ledger_file = os.path.join(root_dir, "asset_ledger.json")
        
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.gen_dir, exist_ok=True)
        
        if not os.path.exists(self.ledger_file):
            self._save_ledger({})

    def _load_ledger(self):
        try:
            with open(self.ledger_file, "r") as f: return json.load(f)
        except: return {}

    def _save_ledger(self, data):
        with open(self.ledger_file, "w") as f: json.dump(data, f, indent=4)

    def save_upload(self, file_obj, context_tag):
        file_obj.seek(0)
        safe_name = f"{datetime.now().strftime('%H%M%S')}_{file_obj.name}"
        save_path = os.path.join(self.upload_dir, safe_name)
        
        with open(save_path, "wb") as f:
            f.write(file_obj.getbuffer())
        
        ledger = self._load_ledger()
        ledger[safe_name] = {
            "type": "source_image",
            "original_name": file_obj.name,
            "path": save_path,
            "context": context_tag,
            "timestamp": str(datetime.now())
        }
        self._save_ledger(ledger)
        return safe_name

    def save_code(self, filename, code, context_tag):
        save_path = os.path.join(self.gen_dir, filename)
        with open(save_path, "w") as f: f.write(code)
        
        ledger = self._load_ledger()
        ledger[filename] = {
            "type": "html_prototype",
            "path": save_path,
            "context": context_tag,
            "timestamp": str(datetime.now())
        }
        self._save_ledger(ledger)
        return save_path

manager = AssetManager()
MEMORY_FILE = "memory.json"

# --- 3. UTILS ---

def get_memory_string():
    if not os.path.exists(MEMORY_FILE): return ""
    with open(MEMORY_FILE, "r") as f: rules = json.load(f)
    return "\n\n**LEARNED USER RULES:**\n" + "\n".join([f"- {r}" for r in rules]) if rules else ""

def save_memory_rule(rule):
    current = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f: current = json.load(f)
    if rule and rule not in current:
        current.append(rule)
        with open(MEMORY_FILE, "w") as f: json.dump(current, f)
        return True
    return False

def image_to_base64(image_file):
    image_file.seek(0)
    encoded = base64.b64encode(image_file.read()).decode()
    mime = "image/jpeg" if image_file.name.lower().endswith(('.jpg','.jpeg')) else "image/png"
    return f"data:{mime};base64,{encoded}"

def open_local_file(file_path):
    abs_path = os.path.abspath(file_path)
    webbrowser.open(f'file://{abs_path}')

# --- 4. MODEL FINDER ---
def get_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if "models/gemini-1.5-pro-latest" in models: return "models/gemini-1.5-pro-latest"
        for m in models: 
            if "gemini-1.5-pro" in m: return m
        for m in models: 
            if "flash" in m.lower(): return m
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

# --- 5. AI LOGIC (STANDARD + REDESIGN) ---

# def extract_unified_style(files, api_key):
#     """Standard style extraction for 'Create New' mode."""
#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel(get_model())
#     imgs = [Image.open(f) for f in files]
#     prompt = "Analyze these images as a Unified Design System. Extract technical rules (Colors, Fonts, Spacing, Radius). Output ONLY JSON."
#     response = model.generate_content([prompt] + imgs)
#     return response.text.replace("```json", "").replace("```", "")

import tempfile  # <--- Add this to imports

def upload_to_gemini(file_obj, api_key):
    """
    Helper: Saves Streamlit UploadedFile to temp disk, 
    uploads to Gemini File API, then cleans up.
    """
    genai.configure(api_key=api_key)
    
    # Create a temporary file because genai.upload_file requires a path
    suffix = os.path.splitext(file_obj.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_obj.getbuffer())
        tmp_path = tmp.name

    try:
        print(f"Uploading {file_obj.name} to Gemini File API...")
        g_file = genai.upload_file(path=tmp_path, mime_type=file_obj.type)
        return g_file
    finally:
        # Clean up local temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def extract_unified_style(files, api_key):
    """
    Updated: Uploads files to Gemini API first, then extracts style.
    Returns: (style_json_string, list_of_gemini_file_objects)
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(get_model())
    
    gemini_files = []
    
    # 1. Upload all assets to Gemini File API
    for f in files:
        # Reset pointer if it was read before
        f.seek(0)
        g_f = upload_to_gemini(f, api_key)
        gemini_files.append(g_f)
    
    prompt = "Analyze these images as a Unified Design System. Extract technical rules (Colors, Fonts, Spacing, Radius). Output ONLY JSON."
    
    # 2. Pass the file handles directly to the model
    response = model.generate_content([prompt] + gemini_files)
    
    return response.text.replace("```json", "").replace("```", ""), gemini_files

def generate_redesign_code(target_file, style_file, instructions, api_key):
    """
    NEW FUNCTION: Takes 2 images.
    Image 1 (Target): Source of TRUTH for Layout/Content.
    Image 2 (Style): Source of TRUTH for Visuals.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(get_model())
    
    img_target = Image.open(target_file)
    img_style = Image.open(style_file)
    
    memory_str = get_memory_string()
    
    prompt = f"""
    You are a UI Redesign Specialist.
    
    **INPUTS:**
    1. First Image: "TARGET UI" (The structure/content we must keep).
    2. Second Image: "INSPIRATION UI" (The visual style we must apply).
    
    **TASK:**
    Rewrite the code for the TARGET UI, but completely change its visual appearance to match the INSPIRATION UI.
    
    **RULES:**
    - **Keep:** All text content, buttons, navigation links, and general layout structure from the TARGET.
    - **Change:** Colors, fonts, border-radius, shadows, gradients, and spacing to match the INSPIRATION.
    - **Instructions:** {instructions}
    
    {memory_str}
    
    **DESIGN MODE INJECTION:**
    Include the 'Design Mode' script (draggable elements, contenteditable) as standard.
    
    **OUTPUT:**
    Return ONLY valid HTML/TailwindCSS code.
    """
    
    # Passing both images to the model
    response = model.generate_content([prompt, img_target, img_style])
    return response.text.replace("```html", "").replace("```", "")



def refine_existing_code(current_code, feedback, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(get_model())
    prompt = f"Expert Editor. Feedback: '{feedback}'. Code: {current_code}. Return ONLY updated HTML."
    response = model.generate_content(prompt)
    return response.text.replace("```html", "").replace("```", "")

# --- 6. MAIN UI ---
st.sidebar.title("⚙️ Setup")
google_key = st.sidebar.text_input("Google AI Key", type="password").strip()

# --- MODE SELECTOR ---
st.sidebar.divider()
app_mode = st.sidebar.radio("Select Mode", ["🆕 Create New UI", "🎨 Redesign Existing UI"])

st.title(f"🚀 JiVS Auto-Coder: {app_mode}")

# ==========================================================
# MODE 1: REDESIGN EXISTING UI (The New Feature)
# ==========================================================
if app_mode == "🎨 Redesign Existing UI":
    st.markdown("Upload a **Target** (Old UI) and an **Inspiration** (New Style). The AI will merge them.")
    
    col_target, col_style = st.columns(2)
    
    with col_target:
        st.subheader("1. Target UI (Structure)")
        target_file = st.file_uploader("Upload UI to Redesign", type=["png", "jpg"], key="target")
        if target_file:
            st.image(target_file, use_container_width=True)

    with col_style:
        st.subheader("2. Inspiration UI (Style)")
        style_file = st.file_uploader("Upload Brand/Style Ref", type=["png", "jpg"], key="style")
        if style_file:
            st.image(style_file, use_container_width=True)
            
    st.divider()
    instructions = st.text_area("Specific Instructions", "Make it look modern, clean, and match the inspiration colors perfectly.")
    
    if st.button("⚡ Redesign Interface", type="primary"):
        if not target_file or not style_file:
            st.error("Please upload BOTH images.")
        elif not google_key:
            st.error("Missing API Key")
        else:
            with st.spinner("Analyzing Structure vs Style..."):
                code = generate_redesign_code(target_file, style_file, instructions, google_key)
                st.session_state['gen_code'] = code
                
                # Save
                fname = "redesigned_ui.html"
                saved_path = manager.save_code(fname, code, "Redesign Task")
                st.session_state['last_saved_path'] = saved_path
                st.rerun()

# ==========================================================
# MODE 2: CREATE NEW UI (The Original Feature)
# ==========================================================
else: 
    col_input, col_build = st.columns([1, 1.3])
    
    with col_input:
        st.subheader("1. Assets & Context")
        uploaded_files = st.file_uploader("Upload Assets", accept_multiple_files=True)
        
        if uploaded_files and google_key:
            st.divider()
            st.write("📝 **Define Context**")
            for f in uploaded_files:
                col_thumb, col_text = st.columns([1, 3])
                col_thumb.image(f, width=60)
                default_val = st.session_state.get(f"txt_{f.name}", "")
                st.text_input(f"Context for {f.name}", value=default_val, key=f"txt_{f.name}", placeholder="e.g. Logo, Dashboard")

            if st.button("🔐 Lock & Save Assets"):
                with st.spinner("Extracting style..."):
                    # style = extract_unified_style(uploaded_files, google_key)
                    style, gemini_files = extract_unified_style(uploaded_files, google_key)        
                    st.session_state['gemini_files'] = gemini_files
                    st.session_state['style_json'] = style
                    for f in uploaded_files:
                        ctx = st.session_state.get(f"txt_{f.name}", "")
                        manager.save_upload(f, ctx)
                    st.success("Assets Saved!")

    with col_build:
        st.subheader("2. Generation")
        user_req = st.text_area("Requirement", "Create a Landing Page with the Company Logo in header.")
        
        if st.button("⚡ Generate Prototype", type="primary"):
            if not google_key:
                st.error("Missing API Key")
            else:
                if 'style_json' not in st.session_state:
                    with st.spinner("Auto-locking styles..."):
                        # style = extract_unified_style(uploaded_files, google_key)
                        style, gemini_files = extract_unified_style(uploaded_files, google_key)        
                        st.session_state['gemini_files'] = gemini_files
                        st.session_state['style_json'] = style

                final_contexts = []
                logo_obj = None
                for f in uploaded_files:
                    live_context = st.session_state.get(f"txt_{f.name}", "")
                    final_contexts.append(live_context)
                    if "logo" in live_context.lower(): logo_obj = f
                
                with st.spinner("Coding..."):
                    code = generate_standard_code(
                        user_req, 
                        st.session_state['style_json'], 
                        final_contexts, 
                        logo_obj, 
                        gemini_files,
                        google_key
                    )
                    st.session_state['gen_code'] = code
                    saved_path = manager.save_code("generated_prototype.html", code, user_req)
                    st.session_state['last_saved_path'] = saved_path
                    st.rerun()

# ==========================================================
# SHARED RESULT VIEW (For both modes)
# ==========================================================
if 'gen_code' in st.session_state:
    st.divider()
    st.subheader("3. Result & Refinement")
    
    # FULLSCREEN BUTTON
    if 'last_saved_path' in st.session_state:
        if st.button("🌍 Open in Browser (Fullscreen)"):
            open_local_file(st.session_state['last_saved_path'])
    
    st.components.v1.html(st.session_state['gen_code'], height=600, scrolling=True)
    st.download_button("Download HTML", st.session_state['gen_code'], "jivs.html", "text/html")
    
    # REFINEMENT & LEARNING
    col_vis, col_train = st.columns([1, 1])
    with col_vis:
        st.markdown("##### Visual Edit")
        st.info("Use '🛠️ Design Mode' inside preview -> Copy Code -> Paste here.")
        pasted_code = st.text_area("Paste updated HTML here", height=100)
        if st.button("💾 Save Visual Changes"):
            if pasted_code and "<html" in pasted_code:
                st.session_state['gen_code'] = pasted_code
                manager.save_code("refined_ui.html", pasted_code, "Refinement")
                st.rerun()

    with col_train:
        st.markdown("##### AI Feedback")
        feedback = st.text_input("Prompt Feedback (e.g. 'Make font bigger')")
        if st.button("🔄 Regenerate"):
            with st.spinner("Refining..."):
                new_code = refine_existing_code(st.session_state['gen_code'], feedback, google_key)
                st.session_state['gen_code'] = new_code
                manager.save_code("refined_ai.html", new_code, feedback)
                st.rerun()