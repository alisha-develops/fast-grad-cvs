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