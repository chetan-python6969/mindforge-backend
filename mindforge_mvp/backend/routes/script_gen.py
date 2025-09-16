from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/generate")
def generate_script(niche: str = "motivation"):
    # Free mock script for demo purposes
    script_text = f"Hey there! This is a 60-second YouTube Short about {niche}. Stay tuned!"
    
    # Save to temp file
    os.makedirs("assets/temp", exist_ok=True)
    script_file = "assets/temp/script.txt"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(script_text)
    
    return {"script": script_text, "file": script_file}
