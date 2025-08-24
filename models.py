from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # 'admin' or 'student'

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    roll_no = Column(String, unique=True, index=True)
    name = Column(String)
    father_name = Column(String)
    branch = Column(String)
    semester = Column(Integer)
    sgpa = Column(Float)
    cgpa = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)

    subjects = relationship("Subject", back_populates="student")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    semester = Column(Integer)
    subject_code = Column(String)
    subject_name = Column(String)
    credits = Column(Float)
    grade = Column(String)
    grade_point = Column(Integer)
    credit_points = Column(Float)

    student = relationship("Student", back_populates="subjects")
