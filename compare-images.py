import base64
import json
import os
from openai import OpenAI


api_key = OPENAPI_KEY
client = OpenAI(api_key=api_key)

# Function to encode the image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def compare_images_openai(image_path_1, image_path_2, output_file="similarity.json"):
    try:
        print(f"Encoding images...\n1: {image_path_1}\n2: {image_path_2}")
        
        # 2. ENCODE IMAGES
        base64_image1 = encode_image(image_path_1)
        base64_image2 = encode_image(image_path_2)

        # 3. DEFINE PROMPT
        system_prompt = """
        Analyze these two web page screenshots and compare them based *only* on their screen graphics and design language.

        Your task:
        1.  Compare the following specific visual elements:
            *   **Font:** Are the font color and style similar?
            *   **Logo:** Are the logos the same?
            *   **Logo Position:** Is the logo on the same side (left/right) on both pages?
            *   **Background Color:** Are the primary background colors similar?
        2.  Determine a "similarity_score" from 0 to 100, where 100 means the specified visual elements are identical.
        3.  List the specific visual features that are similar.
        4.  List the specific visual features that are not similar.

        **Important:** Exclude analysis of content, purpose, or overall layout structure. Focus strictly on the graphical elements mentioned above. For example, do NOT mention differences like "one is a university website and the other is a career page."

        Output Requirement:
        Return ONLY a raw JSON object. Do not include markdown formatting (like ```json).
        The JSON must follow this structure:
        {
            "similarity_score": <integer>,
            "similar_features": ["feature 1", "feature 2", ...],
            "dissimilar_features": ["feature 1", "feature 2", ...]
        }
        """

        user_prompt = "Analyze these two images. Identify features that are similar and not similar, and give a similarity score."

        # 4. SEND REQUEST
        print("Sending request to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image1}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image2}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}, # Enforces JSON output
            max_tokens=1000
        )

        # 5. PROCESS AND SAVE
        json_content = response.choices[0].message.content
        data = json.loads(json_content)

        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Success! Analysis saved to {output_file}")
        print(f"Similarity Score: {data.get('similarity_score')}/100")

    except Exception as e:
        print(f"An error occurred: {e}")

# --- EXECUTION ---
if __name__ == "__main__":
    # Replace with your actual file names
    file1 = "image1.png"
    file2 = "image2.png"
    
    compare_images_openai(file1, file2)