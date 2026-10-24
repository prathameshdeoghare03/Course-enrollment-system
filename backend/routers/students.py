
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import crud
import schema
from database import get_db

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# GET: List all students
@router.get("/", response_model=list[schema.StudentResponse])
def list_students(db: Session = Depends(get_db)):
    return crud.get_students(db)


# GET: Get one student
@router.get("/{student_id}", response_model=schema.StudentResponse)
def read_student(student_id: int, db: Session = Depends(get_db)):
    return crud.get_student(db, student_id)


# POST: Register a student
@router.post(
    "/",
    response_model=schema.StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def add_student(data: schema.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db, data)


# PUT: Update a student
@router.put("/{student_id}", response_model=schema.StudentResponse)
def edit_student(
    student_id: int,
    data: schema.StudentUpdate,
    db: Session = Depends(get_db)
):
    return crud.update_student(db, student_id, data)


# DELETE: Remove a student
@router.delete("/{student_id}")
def remove_student(student_id: int, db: Session = Depends(get_db)):
    return crud.delete_student(db, student_id)
