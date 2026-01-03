import os
import requests
import io
import time
import sys
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Ensure the console can handle emojis
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


# --- Configuration & Pathing ---
# Grab your token from https://huggingface.co/settings/tokens
HF_TOKEN = os.getenv("HF_TOKEN")
# Use whichever token is available, or fallback to token2 if token1 is placeholder

MODEL_ID = "black-forest-labs/FLUX.1-schnell"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

# Directories based on your setup
PROMPT_FILE = Path("Backend/Files/ImageGeneration.Data")
SAVE_DIR = Path("Data")

def gemini(prompt_input: str):
    """
    Main function that cleaned the prompt and triggers generation.
    """
    # 1. Clean the input more thoroughly
    clean_prompt = prompt_input.lower()
    for trigger in ["generate image", "generate a image", "generate", "image of", "image"]:
        clean_prompt = clean_prompt.replace(trigger, "")
    clean_prompt = clean_prompt.strip()
    
    if not clean_prompt:
        print("Empty prompt, skipping generation.")
        return

    # 2. Sync with your data file
    try:
        PROMPT_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROMPT_FILE.write_text(clean_prompt, encoding="utf-8")
        
        # 3. Pull the prompt BACK from the file (mimicking original logic)
        prompt_from_file = PROMPT_FILE.read_text(encoding="utf-8").strip()

        # 4. Generate & Save
        generate_and_save(prompt_from_file)
    except Exception as e:
        print(f"File error in gemini: {e}")

def generate_and_save(prompt: str):
    """Hits the HF API and saves the result in /Data."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"🎨 Generating image for: '{prompt}'...")

    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
        
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            
            # Timestamped filename
            timestamp = int(time.time())
            file_name = f"img_{timestamp}.png"
            file_path = SAVE_DIR / file_name
            
            image.save(file_path)
            print(f"✨ Success! Image saved to: {file_path}")
            
            # Open the image automatically
            if os.name == 'nt':
                os.startfile(str(file_path.absolute()))
        
        elif response.status_code == 401:
            print("💀 API Error: Your Hugging Face token is expired or invalid. Please update it in the .env file.")
        elif response.status_code == 503:
            print("⏳ Model is loading on Hugging Face. Please try again in a few seconds.")
        else:
            print(f"💀 API Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"🚫 Connection error: {e}")

