import pyautogui
import time
import os

# --- Config ---
FILE_PATH = r'Backend\Files\VideoGeneration.Data'
QUERY_BOX_COORDS = (447, 196)
LEONARDO_URL = "https://app.leonardo.ai/image-generation/video"

def ignite_automation(query=None): # Added query parameter
    # If a specific query is passed, we overwrite the file to ensure we only generate that one
    if query:
        # Clean the query (removing 'video' prefix if it exists)
        clean_query = query.replace("video", "").strip()
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(clean_query)
        print(f"Query locked in: {clean_query}")

    # 1. Validation
    if not os.path.exists(FILE_PATH):
        print(f"L + Ratio: {FILE_PATH} doesn't exist.")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]

    if not prompts:
        print("File's empty. No content to cook with.")
        return

    # 2. Launch Sequence
    pyautogui.hotkey('win', '4')
    time.sleep(2) 
    pyautogui.hotkey('ctrl', 't')
    time.sleep(2)
    pyautogui.write(LEONARDO_URL)
    pyautogui.press('enter')
    time.sleep(13) # Give it extra time for the UI to load

    # 3. Execution Loop
    for prompt in prompts:
        pyautogui.click(QUERY_BOX_COORDS[0], QUERY_BOX_COORDS[1])
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.write(prompt, interval=0.01)
        pyautogui.press('enter')
        time.sleep(3)

    print("Video generation initiated successfully.")
