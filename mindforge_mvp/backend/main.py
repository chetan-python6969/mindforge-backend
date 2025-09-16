from fastapi import FastAPI
from .routes import script_gen, voice_gen
from .routes import script_gen, voice_gen, visuals_gen
from .routes import script_gen, voice_gen, visuals_gen, pipeline  # add pipeline



app = FastAPI(title="MindForge MVP")
app.include_router(visuals_gen.router, prefix="/visuals")
app.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])


app.include_router(script_gen.router, prefix="/script")
app.include_router(voice_gen.router, prefix="/voice")

@app.get("/")
def root():
    return {"msg": "MindForge MVP running 🚀"}
