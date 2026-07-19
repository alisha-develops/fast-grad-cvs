from fastapi import FastAPI, Request, HTTPException, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import or_
from dotenv import load_dotenv
from pathlib import Path
import os

from backend.core.database import SessionLocal, Base, engine
from backend.models.student import Student
from backend.schemas.submission import StudentSubmission

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SESSION_SECRET = os.getenv("SESSION_SECRET")

if not ADMIN_PASSWORD:
    raise RuntimeError("ADMIN_PASSWORD is not set in environment variables")
if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET is not set in environment variables")

app.add_middleware(SessionMiddleware, secret_key = SESSION_SECRET)

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount(
    "/frontend",
    StaticFiles(directory=BASE_DIR / "frontend"),
    name="frontend"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "backend" / "templates"
)

def require_admin(request: Request):
    is_logged_in = request.session.get("admin")
    if not is_logged_in:
        raise HTTPException(status_code=307, headers={"Location": "/admin/login"})

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="form.html"
    )

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request, err: str = None):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": err}
    )

@app.post("admin/login")
def admin_login_submit(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["admin"] = True
        return RedirectResponse(url="/admin", status_code=302)
    else:
        return RedirectResponse(url="/admin/login?err=1", status_code=302)
    
@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)

@app.get("/admin", response_class=HTMLResponse)
def admin(
    request:Request,
    search: str = None,
    program: str = None,
    auth=Depends(require_admin)
):
    db = SessionLocal()
    query = db.query(Student)
    if search:
        search_term = "%"+ search +"%"
        query = query.filter(
            or_(
                Student.full_name.ilike(search_term),
                Student.student_id.ilike(search_term),
                Student.email.ilike(search_term),
            )
        )
    if program:
            query = query.filter(Student.degree_program == program)

    students = query.all()

    all_programs = db.query(Student.degree_program).distinct().all()
    program_list = []
    for row in all_programs:
        if row[0]:
            program_list.append(row[0])
    program_list.sort()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "students": students,
            "programs": program_list,
            "search": search or "",
            "selected_program": program or ""
        }
    )


@app.post("/submit")
def submit(student: StudentSubmission):
    db = SessionLocal()

    new_student = Student(
        full_name=student.fullName,
        student_id=student.studentId,
        email=student.email,
        phone=student.phone,
        cgpa=student.cgpa,
        degree_program=student.degreeProgram,
        linkedin=student.linkedin,
        portfolio=student.portfolio,
        objective=student.objective
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
def preview_student(request: Request, db_id: int, _: None = Depends(require_admin)):
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

