from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pathlib import Path

from app.database import engine, Base
from app.models import *  # ensure all models are registered
from app.routers import auth, quiz, pdf, chatbot, cv_analysis, reports, notes
from app.config import settings

# Create all DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Interactive Educational Application in Odontogenic Oral Pathology",
    version="1.0.0",
)

# Static files & templates
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))

# Register API routers
app.include_router(auth.router)
app.include_router(quiz.router)
app.include_router(pdf.router)
app.include_router(chatbot.router)
app.include_router(cv_analysis.router)
app.include_router(reports.router)
app.include_router(notes.router)


# ── Page Routes ──────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/student", response_class=HTMLResponse)
def student_dashboard(request: Request):
    return templates.TemplateResponse("student_dashboard.html", {"request": request})


@app.get("/faculty", response_class=HTMLResponse)
def faculty_dashboard(request: Request):
    return templates.TemplateResponse("faculty_dashboard.html", {"request": request})


@app.get("/quiz/{quiz_id}", response_class=HTMLResponse)
def quiz_page(request: Request, quiz_id: int):
    return templates.TemplateResponse("quiz.html", {"request": request, "quiz_id": quiz_id})


@app.get("/cv-analysis", response_class=HTMLResponse)
def cv_page(request: Request):
    return templates.TemplateResponse("cv_analysis.html", {"request": request})


@app.get("/ar-viewer", response_class=HTMLResponse)
def ar_page(request: Request):
    return templates.TemplateResponse("ar_viewer.html", {"request": request})


@app.get("/3d-models", response_class=HTMLResponse)
def models_3d_page(request: Request):
    return templates.TemplateResponse("3d_models.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
