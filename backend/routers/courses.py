
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import crud
import schema
from database import get_db

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


# GET: List all courses
@router.get("/", response_model=list[schema.CourseResponse])
def list_courses(db: Session = Depends(get_db)):
    return crud.get_courses(db)


# GET: Get one course
@router.get("/{course_id}", response_model=schema.CourseResponse)
def read_course(course_id: int, db: Session = Depends(get_db)):
    return crud.get_course(db, course_id)


# POST: Create a course
@router.post(
    "/",
    response_model=schema.CourseResponse,
    status_code=status.HTTP_201_CREATED
)
def add_course(data: schema.CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db, data)


# PUT: Update a course
@router.put("/{course_id}", response_model=schema.CourseResponse)
def edit_course(
    course_id: int,
    data: schema.CourseUpdate,
    db: Session = Depends(get_db)
):
    return crud.update_course(db, course_id, data)


# DELETE: Remove a course
@router.delete("/{course_id}")
def remove_course(course_id: int, db: Session = Depends(get_db)):
    return crud.delete_course(db, course_id)
