from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from backend.core.database import SessionLocal, Base, engine
from backend.models.student import Student
from backend.schemas.submission import StudentSubmission, StudentOut
from typing import List
from fastapi import HTTPException


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

@app.get("/admin", response_class=HTMLResponse)
def admin(request:Request):
    db = SessionLocal()
    students = db.query(Student).all()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"students": students}
    )


@app.post("/submit")
def submit(student: StudentSubmission):
    db = SessionLocal()

    new_student = Student(
        full_name=student.fullName,
        student_id = student.studentId,
        email = student.email,
        phone = student.phone,
        cgpa = student.cgpa,
        degree_program = student.degreeProgram,
        linkedin = student.linkedin,
        portfolio = student.portfolio,
        objective = student.objective
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    db.close()

    return {
        "message": "Saved!",
        "id": new_student.id
    }


@app.get("/admin/preview/{db_id}", response_class=HTMLResponse)
def preview_student(request: Request, db_id: int):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == db_id).first()
    db.close()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return templates.TemplateResponse(
        request=request,
        name="preview.html",
        context={"student": student, "printable": True}
    )