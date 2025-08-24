from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas, auth, parser
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Middleware
origins = [
    "http://localhost:3000",  # For local Next.js development
    "https://your-vercel-frontend-url.vercel.app", # Replace with your Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: auth.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/upload-pdf/")
def upload_pdf(file: UploadFile = File(...), current_user: schemas.User = Depends(auth.get_current_active_admin), db: Session = Depends(get_db)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    # Save the uploaded file temporarily
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    try:
        student_data = parser.extract_student_data_from_pdf(file_path)
        if not student_data:
            raise HTTPException(status_code=400, detail="Could not extract any student data from the PDF.")
        
        crud.create_student_records(db, student_data)
        return {"message": f"Successfully uploaded and processed {len(student_data)} student records."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        # Clean up the temporary file
        import os
        os.remove(file_path)

@app.get("/students/{roll_no}", response_model=schemas.Student)
def read_student(roll_no: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    # Allow admin to see any student, but students to only see their own
    if current_user.role == 'student' and current_user.username != roll_no:
        raise HTTPException(status_code=403, detail="You can only view your own results.")
    
    db_student = crud.get_student_by_roll_no(db, roll_no=roll_no)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@app.get("/topper/", response_model=schemas.Student)
def read_topper(db: Session = Depends(get_db)):
    topper = crud.get_topper(db)
    if topper is None:
        raise HTTPException(status_code=404, detail="Topper data not available yet.")
    return topper

@app.get("/subject-averages/{semester}")
def read_subject_averages(semester: int, db: Session = Depends(get_db)):
    averages = crud.get_subject_averages(db, semester=semester)
    if not averages:
        raise HTTPException(status_code=404, detail=f"No data found for semester {semester}")
    return averages
