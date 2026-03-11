import sys
from pathlib import Path

# Add src and root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import parse

app = FastAPI(
    title="Tax Parser API",
    description="API for extracting data from tax form PDFs",
    version="1.0.0",
)

# CORS middleware for nice UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup routers
app.include_router(parse.router, prefix="/api", tags=["Parser"])

# Setup Jinja2 templates for UI
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/")
def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    # Make sure to run from project root: python -m src.api.main
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
