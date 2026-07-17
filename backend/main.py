from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from backend.schemas.submission import StudentSubmission

load_dotenv()

app = FastAPI()

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount(
    "/frontend",
    StaticFiles(directory=BASE_DIR / "frontend"),
    name="frontend"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "backend" / "templates"
)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="form.html"
    )


@app.post("/submit")
def submit(student: StudentSubmission):
    print(student.fullName)

    return {
        "message": "Received!",
        "name": student.fullName
    }