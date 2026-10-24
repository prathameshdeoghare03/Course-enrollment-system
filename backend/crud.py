from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

import models
import schema


# ========== COURSE CRUD ==========

def get_courses(db: Session):
    return db.query(models.Course).all()


def get_course(db: Session, course_id: int):
    course = (
        db.query(models.Course)
        .filter(models.Course.id == course_id)
        .first()
    )

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


def create_course(db: Session, data: schema.CourseCreate):
    course = models.Course(
        title=data.title,
        instructor=data.instructor,
        capacity=data.capacity,
        seats_available=data.capacity,
        fee=data.fee
    )

    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(
    db: Session,
    course_id: int,
    data: schema.CourseUpdate
):
    course = get_course(db, course_id)
    changes = data.model_dump(exclude_unset=True)

    if "capacity" in changes:
        new_capacity = changes["capacity"]

        if new_capacity is not None:
            occupied = course.capacity - course.seats_available

            if new_capacity < occupied:
                raise HTTPException(
                    status_code=400,
                    detail="Capacity cannot be less than occupied seats"
                )

            course.seats_available = new_capacity - occupied
            course.capacity = new_capacity

    for key, value in changes.items():
        if key != "capacity" and value is not None:
            setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int):
    course = get_course(db, course_id)

    history = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.course_id == course_id)
        .first()
    )

    if history is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a course with enrollment history"
        )

    db.delete(course)
    db.commit()

    return {"message": "Course deleted successfully"}


# ========== STUDENT CRUD ==========

def get_students(db: Session):
    return db.query(models.Student).all()


def get_student(db: Session, student_id: int):
    student = (
        db.query(models.Student)
        .filter(models.Student.id == student_id)
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


def create_student(db: Session, data: schema.StudentCreate):
    existing = (
        db.query(models.Student)
        .filter(models.Student.email == str(data.email))
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    student = models.Student(
        name=data.name,
        email=str(data.email)
    )

    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(
    db: Session,
    student_id: int,
    data: schema.StudentUpdate
):
    student = get_student(db, student_id)
    changes = data.model_dump(exclude_unset=True)

    if "email" in changes and changes["email"] is not None:
        email = str(changes["email"])

        existing = (
            db.query(models.Student)
            .filter(
                models.Student.email == email,
                models.Student.id != student_id
            )
            .first()
        )

        if existing is not None:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        changes["email"] = email

    for key, value in changes.items():
        if value is not None:
            setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: int):
    student = get_student(db, student_id)

    history = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.student_id == student_id)
        .first()
    )

    if history is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a student with enrollment history"
        )

    db.delete(student)
    db.commit()

    return {"message": "Student deleted successfully"}


# ========== ENROLLMENT OPERATIONS ==========

def enroll_student(db: Session, data: schema.EnrollmentCreate):
    student = get_student(db, data.student_id)

    # Lock the course row before checking available seats.
    course = (
        db.query(models.Course)
        .filter(models.Course.id == data.course_id)
        .with_for_update()
        .first()
    )

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Check for an existing active enrollment.
    existing = (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.student_id == student.id,
            models.Enrollment.course_id == course.id,
            models.Enrollment.status == "active"
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Student is already enrolled in this course"
        )

    if course.seats_available <= 0:
        raise HTTPException(
            status_code=400,
            detail="Course is full"
        )

    course.seats_available -= 1

    enrollment = models.Enrollment(
    student_id=student.id,
    course_id=course.id,
    enrollment_date=datetime.now(),
    status="active"
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment


def get_student_enrollments(db: Session, student_id: int):
    get_student(db, student_id)

    return (
        db.query(models.Enrollment)
        .filter(models.Enrollment.student_id == student_id)
        .all()
    )


def get_course_enrollments(db: Session, course_id: int):
    get_course(db, course_id)

    return (
        db.query(models.Enrollment)
        .filter(models.Enrollment.course_id == course_id)
        .all()
    )


def cancel_enrollment(db: Session, enrollment_id: int):
    enrollment = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.id == enrollment_id)
        .with_for_update()
        .first()
    )

    if enrollment is None:
        raise HTTPException(
            status_code=404,
            detail="Enrollment not found"
        )

    if enrollment.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Enrollment is already cancelled"
        )

    course = (
        db.query(models.Course)
        .filter(models.Course.id == enrollment.course_id)
        .with_for_update()
        .first()
    )

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    enrollment.status = "cancelled"
    course.seats_available = min(
        course.seats_available + 1,
        course.capacity
    )

    db.commit()
    db.refresh(enrollment)

    return enrollment
