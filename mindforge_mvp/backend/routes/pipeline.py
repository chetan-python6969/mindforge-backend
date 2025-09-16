from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Optional, List, Dict
import os
import tempfile
import uuid
import time
import logging
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import shutil
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Monkey patch for Pillow >=10.0 compatibility
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# Set up logging with job ID
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - [%(job_id)s] - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration from environment variables
VIDEO_RESOLUTION = tuple(map(int, os.getenv("VIDEO_RESOLUTION", "720,1280").split(",")))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "24"))
FONT_SIZE = int(os.getenv("FONT_SIZE", "28"))
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "28"))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "60"))

# Simple in-memory rate limiter
request_times: List[float] = []

@contextmanager
def pipeline_context(job_id: str):
    """
    Context manager to add job_id to logging context.
    """
    logger_extra = logging.LoggerAdapter(logger, {"job_id": job_id})
    try:
        yield logger_extra
    finally:
        pass

def generate_script(niche: str, job_id: str) -> str:
    """
    Generate a 40-60 second YouTube Shorts script using OpenAI or a fallback mock script.
    """
    with pipeline_context(job_id) as log:
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai
                openai.api_key = openai_key
                prompt = f"Write an engaging 40-60 second YouTube Shorts script about {niche}. Use short sentences and include a hook."
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                )
                script = response.choices[0].message.content.strip()
                log.info(f"Generated script for niche '{niche}': {script[:50]}...")
                return script
            except Exception as e:
                log.error(f"OpenAI script generation failed: {e}")
                return f"Auto script fallback for {niche}. This is a 50-second short. Hook: listen up! Key points about {niche}..."
        return f"Hey! Here's a quick short about {niche}. Hook: stay sharp. Tip one. Tip two. Final push to take action!"

def text_to_speech(text: str, output_path: str, job_id: str) -> None:
    """
    Convert text to speech using gTTS and save to output_path.
    """
    with pipeline_context(job_id) as log:
        try:
            tts = gTTS(text=text, lang="en")
            tts.save(output_path)
            log.info(f"Generated audio: {output_path}")
        except Exception as e:
            log.error(f"Text-to-speech conversion failed: {e}")
            raise

def wrap_text(text: str, max_chars: int = MAX_TEXT_CHARS) -> List[str]:
    """
    Wrap text into lines with a maximum character limit.
    """
    words = text.split