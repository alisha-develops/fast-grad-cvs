from pydantic import BaseModel
from typing import Optional

class StudentSubmission(BaseModel):
    fullName: str
    studentId: str
    email: str
    phone: str
    cgpa: str
    degreeProgram: str
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    objective: str
    education: str
    fypTitle: str
    fypDesc: str
    fypSupervisor: str
    electiveCourses: str
    areasOfInterest: str
    technicalSkills: str
    personalSkills: str
    certifications: Optional[str] = None
    honors: Optional[str] = None
    internship: str
    leadership: str
    photoUrl: Optional[str] = None