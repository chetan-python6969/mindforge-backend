from fastapi import APIRouter
import os
from diffusers import StableDiffusionPipeline
import torch

router = APIRouter()

# Lite model for CPU testing
model_id = "runwayml/stable-diffusion-v1-5"
device = "cpu"  # force CPU
pipe = StableDiffusionPipeline.from_pretrained(model_id)
pipe = pipe.to(device)

@router.post("/generate")
def generate_visuals():
    script_file = "assets/temp/script.txt"
    if not os.path.exists(script_file):
        return {"status": "error", "message": "No script found."}
    
    with open(script_file, "r", encoding="utf-8") as f:
        lines = f.read().split(".")
    
    output_dir = "outputs/test_channel/images"
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []

    for idx, line in enumerate(lines):
        if not line.strip():
            continue
        prompt = f"{line.strip()}, YouTube short style, simple cartoonish"
        # Lite settings
        image = pipe(prompt, num_inference_steps=10, height=256, width=256).images[0]
        path = os.path.join(output_dir, f"image_{idx+1}.png")
        image.save(path)
        image_paths.append(path)
    
    return {"status": "success", "images": image_paths}
