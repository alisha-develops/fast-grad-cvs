from sqlalchemy import Column, Integer, String, Text
from backend.core.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    student_id = Column(String)
    email = Column(String)
    phone = Column(String)
    cgpa = Column(String)
    degree_program = Column(String)
    linkedin = Column(String)
    portfolio = Column(String)
    objective = Column(Text)