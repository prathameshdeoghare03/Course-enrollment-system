
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import crud
import models
import schema
from database import get_db

router = APIRouter(tags=["Enrollments"])


# POST: Enroll a student in a course
@router.post(
    "/enroll",
    response_model=schema.EnrollmentResponse,
    status_code=status.HTTP_201_CREATED
)
def enroll_student(
    data: schema.EnrollmentCreate,
    db: Session = Depends(get_db)
):
    return crud.enroll_student(db, data)


# GET: View all enrollments
@router.get(
    "/enrollments/",
    response_model=list[schema.EnrollmentResponse]
)
def get_all_enrollments(db: Session = Depends(get_db)):
    return db.query(models.Enrollment).all()


# GET: View all enrollments for a student
@router.get(
    "/enrollments/student/{student_id}",
    response_model=list[schema.EnrollmentResponse]
)
def get_student_enrollments(
    student_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_student_enrollments(db, student_id)


# GET: View all enrollments for a course
@router.get(
    "/enrollments/course/{course_id}",
    response_model=list[schema.EnrollmentResponse]
)
def get_course_enrollments(
    course_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_course_enrollments(db, course_id)


# DELETE: Cancel an enrollment without deleting its history
@router.delete(
    "/enrollments/{enrollment_id}",
    response_model=schema.EnrollmentResponse
)
def cancel_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    return crud.cancel_enrollment(db, enrollment_id)
