from pydantic import BaseModel
from typing import Optional

class StudentSubmission(BaseModel):
    fullName: str
    studentId: str
    email:str
    phone: str
    cgpa: str
    degreeProgram: str
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    objective: str

class StudentOut(BaseModel):
    id: int
    full_name: str
    student_id: str
    email: str
    phone: str
    cgpa: str
    degree_program: str
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    objective: str

    class Config:
        from_attributes = True