from sqlalchemy import Column, Integer, String, Text
from backend.database import Base

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
    education = Column(Text)
    fyp_title = Column(String)
    fyp_title = Column(String)
    fyp_desc = Column(Text)
    fyp_supervisor = Column(String)
    elective_courses = Column(Text)
    areas_of_interest = Column(Text)
    techincal_skills = Column(Text)
    Certifications = Column(Text)
    Personal_skilss = Column(Text)
    honors = Column(Text)
    internship = Column(Text)
    leadership = Column(Text)