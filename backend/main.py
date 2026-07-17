from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from backend.core.database import SessionLocal, Base, engine
from backend.models.student import Student
from backend.schemas.submission import StudentSubmission
from backend.core.database import Base, engine


Base.metadata.create_all(bind=engine)

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
    db = SessionLocal()

    new_student = Student(
        full_name=student.fullName
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    db.close()

    return {
        "message": "Saved!",
        "id": new_student.id
    }