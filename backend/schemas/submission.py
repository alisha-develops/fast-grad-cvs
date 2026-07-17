from pydantic import BaseModel

class StudentSubmission(BaseModel):
    fullName: str