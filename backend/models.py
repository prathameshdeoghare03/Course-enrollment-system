
from datetime import datetime

from sqlalchemy import String, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    instructor: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    capacity: Mapped[int] = mapped_column(nullable=False)
    seats_available: Mapped[int] = mapped_column(nullable=False)
    fee: Mapped[float] = mapped_column(Float, nullable=False)

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course"
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False
    )

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="student"
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"), nullable=False
    )

    enrollment_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False
    )

    student: Mapped["Student"] = relationship(
        back_populates="enrollments"
    )
    course: Mapped["Course"] = relationship(
        back_populates="enrollments"
    )
