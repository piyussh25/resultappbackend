from pydantic import BaseModel
from typing import List, Optional

# Subject Schemas
class SubjectBase(BaseModel):
    subject_code: str
    subject_name: str
    credits: float
    grade: str
    grade_point: int
    credit_points: float

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: int
    semester: int

    class Config:
        orm_mode = True

# Student Schemas
class StudentBase(BaseModel):
    roll_no: str
    name: str
    father_name: str
    branch: str
    semester: int
    sgpa: float

class StudentCreate(StudentBase):
    subjects: List[SubjectCreate]

class Student(StudentBase):
    id: int
    cgpa: Optional[float] = None
    rank: Optional[int] = None
    subjects: List[Subject] = []

    class Config:
        orm_mode = True

# User Schemas
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# Token Schemas for JWT
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
