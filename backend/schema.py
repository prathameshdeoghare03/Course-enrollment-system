
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


# ========== COURSE SCHEMAS ==========

class CourseCreate(BaseModel):
    title: str
    instructor: str
    capacity: int
    fee: float


class CourseUpdate(BaseModel):
    title: str | None = None
    instructor: str | None = None
    capacity: int | None = None
    fee: float | None = None


class CourseResponse(BaseModel):
    id: int
    title: str
    instructor: str
    capacity: int
    seats_available: int
    fee: float

    model_config = ConfigDict(from_attributes=True)


# ========== STUDENT SCHEMAS ==========

class StudentCreate(BaseModel):
    name: str
    email: EmailStr


class StudentUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


# ========== ENROLLMENT SCHEMAS ==========

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrollment_date: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)
