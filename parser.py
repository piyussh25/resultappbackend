import pdfplumber
import pandas as pd
import re
from . import schemas

def extract_student_data_from_pdf(file_path: str):
    students_data = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            tables = page.extract_tables()

            # Regex to find student details
            roll_no_match = re.search(r"Roll No\.\s+(\d+)", text)
            name_match = re.search(r"Name\s+([A-Z\s]+)", text)
            father_name_match = re.search(r"Father's Name\s+([A-Z\s]+)", text)
            branch_match = re.search(r"Branch\s+([A-Z\s&]+)", text)
            semester_match = re.search(r"Semester\s+(\d+)", text)
            sgpa_match = re.search(r"SGPA:\s+([\d\.]+)", text)

            if not all([roll_no_match, name_match, father_name_match, branch_match, semester_match, sgpa_match]):
                continue

            student_info = {
                'roll_no': roll_no_match.group(1).strip(),
                'name': name_match.group(1).strip(),
                'father_name': father_name_match.group(1).strip(),
                'branch': branch_match.group(1).strip(),
                'semester': int(semester_match.group(1).strip()),
                'sgpa': float(sgpa_match.group(1).strip()),
            }

            # Find the table with subject data
            for table in tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                if 'Subject Code' in df.columns and 'Credits' in df.columns:
                    subjects = []
                    for _, row in df.iterrows():
                        # Check for valid row
                        if row['Subject Code'] and row['Grade']:
                            try:
                                subjects.append(schemas.SubjectCreate(
                                    subject_code=row['Subject Code'],
                                    subject_name=row.get('Subject Name', ''), # Assuming Subject Name might not be present
                                    credits=float(row['Credits']),
                                    grade=row['Grade'],
                                    grade_point=int(row['Grade Point']),
                                    credit_points=float(row['Credit Points'])
                                ))
                            except (ValueError, TypeError):
                                # Skip rows that can't be parsed
                                continue
                    
                    student_full_data = schemas.StudentCreate(
                        **student_info,
                        subjects=subjects
                    )
                    students_data.append(student_full_data)
                    break # Assume one student per page for simplicity, can be adjusted

    return students_data
