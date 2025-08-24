from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas, auth

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_student_records(db: Session, students: list[schemas.StudentCreate]):
    for student_data in students:
        # Check if student already exists
        db_student = db.query(models.Student).filter(models.Student.roll_no == student_data.roll_no).first()
        if db_student:
            # Optionally, update existing student data or skip
            continue

        db_student = models.Student(
            roll_no=student_data.roll_no,
            name=student_data.name,
            father_name=student_data.father_name,
            branch=student_data.branch,
            semester=student_data.semester,
            sgpa=student_data.sgpa
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)

        for subject_data in student_data.subjects:
            db_subject = models.Subject(**subject_data.dict(), student_id=db_student.id, semester=db_student.semester)
            db.add(db_subject)
        db.commit()
    # After adding new students, update ranks
    update_ranks_and_cgpa(db)

def get_student_by_roll_no(db: Session, roll_no: str):
    return db.query(models.Student).filter(models.Student.roll_no == roll_no).first()

def get_topper(db: Session):
    # Assuming topper is based on highest CGPA, fallback to SGPA
    return db.query(models.Student).order_by(models.Student.cgpa.desc().nullslast(), models.Student.sgpa.desc()).first()

def get_subject_averages(db: Session, semester: int):
    return db.query(
        models.Subject.subject_code,
        models.Subject.subject_name,
        func.avg(models.Subject.grade_point).label('average_grade_point')
    ).filter(models.Subject.semester == semester).group_by(models.Subject.subject_code, models.Subject.subject_name).all()

def update_ranks_and_cgpa(db: Session):
    # This is a simplified example. A real implementation might need to handle different branches separately.
    all_students = db.query(models.Student).order_by(models.Student.sgpa.desc()).all()
    
    # Calculate CGPA (simplified as average of SGPA for now)
    for student in all_students:
        # A more complex calculation would be needed for a real multi-semester system
        student.cgpa = student.sgpa # Placeholder logic

    # Assign ranks
    rank = 1
    for student in all_students:
        student.rank = rank
        rank += 1
    
    db.commit()
