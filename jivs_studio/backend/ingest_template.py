import os
from vector_store import DesignMemory

# Your Template Data (Same as before)
ui_template_data = {
    "UI": {
        "name": "S/4 Transformation Dashboard", 
        "image_path": "new-build-history/UI_Template_001.jpeg",
        "overall_page_description": """A dark-themed dashboard interface for the S/4 Transformation Project. 
        It features a high-contrast dark background (#1e1e1e) with bright call-to-action buttons. 
        Typography is sans-serif, clean, white text. 
        Key visual elements include navigation tabs, system analysis status tables, and performance metrics bars."""
    },
    "elements": [
        {"type": "logo", "desc": "JIVS red circular logo top-left."},
        {"type": "header", "desc": "Main project title 'S/4 Transformation Project'."},
        {"type": "button", "desc": "Large red button 'START ALL ANALYSIS' aligned right."}
    ]
}

def upload_data():
    # This will now use Google Embeddings automatically because we updated vector_store.py
    memory = DesignMemory()
    
    embedding_text = f"""
    Style Name: {ui_template_data['UI']['name']}
    Visual Style: {ui_template_data['UI']['overall_page_description']}
    Key Components: {', '.join([e['type'] for e in ui_template_data['elements']])}
    Theme: Dark Mode, Enterprise, Dashboard, Red Accents.
    """

    metadata = {
        "name": ui_template_data['UI']['name'],
        "image_path": ui_template_data['UI']['image_path'],
        "style_rules": "Background: Dark (#121212), Primary Color: Red (#FF0000)"
    }

    print("Uploading template to Gemini-powered Qdrant...")
    memory.add_template(embedding_text, metadata)

if __name__ == "__main__":
    upload_data()