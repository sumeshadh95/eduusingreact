"""React API backend bootstrap for CoursePilot AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.config import ASSET_DIR, load_environment
from api.routes import router

load_environment()
ASSET_DIR.mkdir(exist_ok=True)

app = FastAPI(title="CoursePilot AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/generated_assets", StaticFiles(directory=ASSET_DIR), name="generated_assets")
app.include_router(router)
