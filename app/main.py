from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.agent import run_agent
from pathlib import Path
import uvicorn
import shutil
import os
import uuid

# Determine if we're running in Vercel or local environment
IS_VERCEL = os.environ.get('VERCEL', False)

# Set up storage directories
if IS_VERCEL:
    # In Vercel, use /tmp directory for storage
    UPLOAD_DIR = "/tmp/uploads"
    STATIC_DIR = "app/static"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
else:
    # Local environment
    UPLOAD_DIR = "app/static/uploads"
    STATIC_DIR = "app/static"
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path("app/static/css").mkdir(parents=True, exist_ok=True)
    Path("app/static/js").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Text Extraction Agent")

# Mount static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/extract")
async def extract_text(
    request: Request,
    image: UploadFile = File(...),
    prompt: str = Form(...)
):
    # Generate a safe filename if the original is None
    safe_filename = image.filename or f"{uuid.uuid4()}.jpg"
    
    # Save the uploaded image
    file_path = str(Path(UPLOAD_DIR) / safe_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Process the image and prompt using the agent
    result = run_agent(file_path, prompt)
    
    # Determine the correct path to use in the response
    image_path = f"/static/uploads/{safe_filename}" if not IS_VERCEL else f"/tmp/uploads/{safe_filename}"
    
    # Prepare the response data
    response_data = {
        "image_path": image_path,
        "extracted_text": result["extracted_text"],
        "result": result["result"][0] if isinstance(result["result"], tuple) else result["result"],
        "prompt": prompt
    }
    
    # Return JSON for AJAX requests or HTML for regular form submission
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax:
        return JSONResponse(content=response_data)
    else:
        return templates.TemplateResponse("index.html", {"request": request, **response_data, "show_results": True})