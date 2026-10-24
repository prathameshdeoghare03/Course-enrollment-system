
from fastapi import FastAPI

from database import Base, engine
from models import Course, Student, Enrollment
from routers import courses, students, enrollments


# Register models with SQLAlchemy metadata
_ = (Course, Student, Enrollment)

# Create database tables
Base.metadata.create_all(bind=engine)


# Initialize FastAPI
app = FastAPI(
    title="Online Course Enrollment System",
    description="Manage courses, students, and enrollments",
    version="1.0.0"
)


# Register API routers
app.include_router(courses.router)
app.include_router(students.router)
app.include_router(enrollments.router)


@app.get("/")
def home():
    return {
        "message": "Online Course Enrollment System API is running",
        "docs": "/docs"
    }
