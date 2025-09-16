from fastapi import APIRouter
from gtts import gTTS
import os

router = APIRouter()

@router.post("/tts")
def text_to_speech():
    script_file = "assets/temp/script.txt"
    if not os.path.exists(script_file):
        return {"status": "error", "message": "No script found. Run /script/generate first."}
    
    with open(script_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    tts = gTTS(text=text, lang="en")
    os.makedirs("outputs/test_channel", exist_ok=True)
    audio_path = "outputs/test_channel/voice.mp3"
    tts.save(audio_path)
    
    return {"status": "success", "voice_file": audio_path}
