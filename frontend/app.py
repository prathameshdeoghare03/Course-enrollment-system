import requests
import streamlit as st
import pandas as pd
from typing import Any, cast
from collections.abc import Mapping

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Course Enrollment System",
    page_icon="🎓",
    layout="wide",
)

# SIDEBAR
try:
    st.sidebar.image("logo.png", width=120)
except (FileNotFoundError, OSError):
    st.sidebar.write("🎓")

st.sidebar.title("Course Enrollment")
st.sidebar.caption("Online Learning Management")

page = st.sidebar.selectbox(
    "Navigate",
    ["Dashboard", "Courses", "Students", "Enrollments"],
)


# API FUNCTIONS
def send_data(
    method: str,
    endpoint: str,
    data: Mapping[str, Any] | None = None,
) -> bool:
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            json=dict(data) if data is not None else None,
            timeout=10,
        )

        if response.status_code in (200, 201, 202, 204):
            return True

        st.error(
            f"Request failed ({response.status_code}): {response.text}"
        )
        return False

    except requests.exceptions.RequestException as exc:
        st.error(f"Cannot connect to FastAPI: {exc}")
        return False


def get_data(endpoint: str) -> list[dict[str, Any]]:
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=10,
        )
        response.raise_for_status()

        result: object = response.json()

        if not isinstance(result, list):
            st.error(f"Unexpected response format from {endpoint}.")
            return []

        raw_items = cast(list[object], result)
        items: list[dict[str, Any]] = []

        for raw_item in raw_items:
            if not isinstance(raw_item, dict):
                continue

            item = cast(dict[str, Any], raw_item)
            typed_item: dict[str, Any] = {}

            for key, value in item.items():
                typed_item[str(key)] = value

            items.append(typed_item)

        return items

    except requests.exceptions.RequestException as exc:
        st.error(f"Unable to load {endpoint}: {exc}")
        return []

    except ValueError:
        st.error(f"Invalid JSON response from {endpoint}.")
        return []


# HELPER FUNCTIONS
def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError, OverflowError):
        return default


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError, OverflowError):
        return default


def as_text(value: Any) -> str:
    return "" if value is None else str(value)


def show_table(rows: list[dict[str, Any]]) -> None:
    if not rows:
        st.info("No records found.")
        return

    df = pd.DataFrame.from_records(rows)
    st.write(df)


# LOAD DATA
courses = get_data("/courses/")
students = get_data("/students/")
enrollments = get_data("/enrollments/")


# DASHBOARD


if page == "Dashboard":

    # ---------- Header ----------
    logo_col, title_col = st.columns([1, 6])

    with logo_col:
        st.image(r"D:\course\frontend\logo.png", width=100)

    with title_col:
        st.title("Course Enrollment System")
        st.caption("ONLINE LEARNING MANAGEMENT")
        st.write(
            "Manage courses, students, enrollments, and seat availability "
            "from one place."
        )

    st.divider()

    # ---------- Dashboard Statistics ----------
    total_courses = len(courses)
    total_students = len(students)
    total_enrollments = len(enrollments)

    available_seats = sum(
        as_int(course.get("seats_available"))
        for course in courses
    )

    total_capacity = sum(
        as_int(course.get("capacity"))
        for course in courses
    )

    occupied_seats = max(0, total_capacity - available_seats)

    seat_utilization = (
        (occupied_seats / total_capacity) * 100
        if total_capacity > 0
        else 0.0
    )

    # ---------- Summary Metrics ----------
    st.subheader("📊 Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📚 Total Courses", total_courses)
    col2.metric("👨‍🎓 Total Students", total_students)
    col3.metric("📝 Enrollments", total_enrollments)
    col4.metric("💺 Available Seats", available_seats)

    st.divider()

    # ---------- Seat Availability ----------
    st.subheader("💺 Seat Availability")

    progress_col, stats_col = st.columns([2, 1])

    with progress_col:
        st.write("Course Capacity Utilization")
        st.progress(
            int(min(100.0, max(0.0, seat_utilization)))
        )
        st.caption(
            f"{seat_utilization:.1f}% of total capacity is occupied"
        )

    with stats_col:
        st.write("**Total Capacity**")
        st.title(f"{total_capacity:,}")
        st.caption(f"{occupied_seats:,} occupied seats")

    st.divider()

    # ---------- Course Availability ----------
    st.subheader("📈 Course-wise Available Seats")

    if courses:
        for course in courses:
            course_title = str(course.get("title", "Untitled"))
            seats = max(0, as_int(course.get("seats_available")))
            capacity = max(0, as_int(course.get("capacity")))

            st.write(f"**{course_title}**")

            if capacity > 0:
                availability_percent = min(100.0, seats / capacity * 100)
                st.progress(int(availability_percent))
                st.caption(
                    f"{seats} of {capacity} seats available "
                    f"({availability_percent:.1f}%)"
                )
            else:
                st.caption(f"{seats} seats available; capacity not set")

    else:
        st.info("No courses available to display.")

    st.divider()

    # ---------- Course List ----------
    st.subheader("📚 Course Management")
    st.caption(
        "Overview of all courses currently registered in the system."
    )

    if courses:
        show_table(courses)
    else:
        st.info(
            "No courses found. Add your first course from the Courses page."
        )

    # ---------- Footer ----------
    st.divider()
    st.caption("Course Enrollment System | Dashboard")




# COURSES
elif page == "Courses":
    st.title("📚 Courses")

    action = st.radio(
        "Choose Action",
        ["Create", "View", "Update", "Delete"],
        horizontal=True,
    )

    if action == "Create":
        with st.form("create_course"):
            title = st.text_input("Course Title")
            instructor = st.text_input("Instructor")
            capacity = st.number_input(
                "Seat Capacity", min_value=1, value=30, step=1
            )
            seats_available = st.number_input(
                "Seats Available", min_value=0, value=30, step=1
            )
            fee = st.number_input(
                "Fee", min_value=0.0, value=0.0, step=100.0
            )
            submitted = st.form_submit_button("Create Course")

        if submitted:
            if not title.strip():
                st.warning("Enter a course title.")
            elif seats_available > capacity:
                st.warning("Available seats cannot exceed capacity.")
            else:
                data: dict[str, Any] = {
                    "title": title.strip(),
                    "instructor": instructor.strip() or None,
                    "capacity": int(capacity),
                    "seats_available": int(seats_available),
                    "fee": float(fee),
                }

                if send_data("POST", "/courses/", data):
                    st.success("Course created successfully.")
                    st.rerun()

    elif action == "View":
        show_table(courses)

    elif action == "Update":
        if courses:
            options = {
                f"{c.get('id')} - {c.get('title')}": c
                for c in courses
            }
            selected = st.selectbox(
                "Select Course", list(options.keys())
            )
            course = options[selected]

            with st.form("update_course"):
                title = st.text_input(
                    "Course Title",
                    value=as_text(course.get("title")),
                )
                instructor = st.text_input(
                    "Instructor",
                    value=as_text(course.get("instructor")),
                )
                capacity = st.number_input(
                    "Seat Capacity",
                    min_value=1,
                    value=max(1, as_int(course.get("capacity"), 1)),
                )
                fee = st.number_input(
                    "Fee",
                    min_value=0.0,
                    value=max(0.0, as_float(course.get("fee"))),
                    step=100.0,
                )
                submitted = st.form_submit_button("Save Changes")

            if submitted:
                if not title.strip():
                    st.warning("Enter a course title.")
                else:
                    data: dict[str, Any] = {
                        "title": title.strip(),
                        "instructor": instructor.strip() or None,
                        "capacity": int(capacity),
                        "fee": float(fee),
                    }

                    if send_data(
                        "PUT",
                        f"/courses/{course.get('id')}",
                        data,
                    ):
                        st.success("Course updated successfully.")
                        st.rerun()
        else:
            st.info("No courses available to update.")

    elif action == "Delete":
        if courses:
            options = {
                f"{c.get('id')} - {c.get('title')}": c
                for c in courses
            }
            selected = st.selectbox(
                "Select Course to Delete", list(options.keys())
            )
            course = options[selected]

            if st.button("Delete Course"):
                if send_data(
                    "DELETE", f"/courses/{course.get('id')}"
                ):
                    st.success("Course deleted successfully.")
                    st.rerun()
        else:
            st.info("No courses available to delete.")


# STUDENTS
elif page == "Students":
    st.title("👨‍🎓 Students")

    action = st.radio(
        "Choose Action",
        ["Register", "View", "Update", "Delete"],
        horizontal=True,
    )

    if action == "Register":
        with st.form("register_student"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Register Student")

        if submitted:
            if not name.strip() or not email.strip():
                st.warning("Enter both name and email.")
            else:
                data: dict[str, Any] = {
                    "name": name.strip(),
                    "email": email.strip(),
                }

                if send_data("POST", "/students/", data):
                    st.success("Student registered successfully.")
                    st.rerun()

    elif action == "View":
        show_table(students)

    elif action == "Update":
        if students:
            options = {
                f"{s.get('id')} - {s.get('name')}": s
                for s in students
            }
            selected = st.selectbox(
                "Select Student", list(options.keys())
            )
            student = options[selected]

            with st.form("update_student"):
                name = st.text_input(
                    "Full Name",
                    value=as_text(student.get("name")),
                )
                email = st.text_input(
                    "Email",
                    value=as_text(student.get("email")),
                )
                submitted = st.form_submit_button("Save Changes")

            if submitted:
                if not name.strip() or not email.strip():
                    st.warning("Enter both name and email.")
                else:
                    data: dict[str, Any] = {
                        "name": name.strip(),
                        "email": email.strip(),
                    }

                    if send_data(
                        "PUT",
                        f"/students/{student.get('id')}",
                        data,
                    ):
                        st.success("Student updated successfully.")
                        st.rerun()
        else:
            st.info("No students available to update.")

    elif action == "Delete":
        if students:
            options = {
                f"{s.get('id')} - {s.get('name')}": s
                for s in students
            }
            selected = st.selectbox(
                "Select Student to Delete", list(options.keys())
            )
            student = options[selected]

            if st.button("Delete Student"):
                if send_data(
                    "DELETE", f"/students/{student.get('id')}"
                ):
                    st.success("Student deleted successfully.")
                    st.rerun()
        else:
            st.info("No students available to delete.")


# ENROLLMENTS
elif page == "Enrollments":
    st.title("📝 Enrollments")

    action = st.radio(
        "Choose Action",
        ["Enroll Student", "View", "Cancel"],
        horizontal=True,
    )

    if action == "Enroll Student":
        available_courses = [
            course
            for course in courses
            if as_int(course.get("seats_available")) > 0
        ]

        if not students:
            st.info("Register a student first.")
        elif not available_courses:
            st.info("No courses have available seats.")
        else:
            student_options = {
                f"{student.get('id')} - {student.get('name')}": student
                for student in students
            }

            course_options = {
                (
                    f"{course.get('id')} - {course.get('title')} "
                    f"({as_int(course.get('seats_available'))} seats left)"
                ): course
                for course in available_courses
            }

            with st.form("enroll_student"):
                selected_student = st.selectbox(
                    "Select Student", list(student_options.keys())
                )
                selected_course = st.selectbox(
                    "Select Course", list(course_options.keys())
                )
                submitted = st.form_submit_button("Enroll Student")

            if submitted:
                student = student_options[selected_student]
                course = course_options[selected_course]

                data: dict[str, Any] = {
                    "student_id": as_int(student.get("id")),
                    "course_id": as_int(course.get("id")),
                }

                if send_data("POST", "/enrollments/", data):
                    st.success("Student enrolled successfully.")
                    st.rerun()

    elif action == "View":
        show_table(enrollments)

    elif action == "Cancel":
        active_enrollments = [
            enrollment
            for enrollment in enrollments
            if as_text(enrollment.get("status")).lower() == "active"
        ]

        if active_enrollments:
            options = {
                (
                    f"Enrollment {enrollment.get('id')} - "
                    f"Student {enrollment.get('student_id')} - "
                    f"Course {enrollment.get('course_id')}"
                ): enrollment
                for enrollment in active_enrollments
            }

            selected = st.selectbox(
                "Select Enrollment", list(options.keys())
            )
            enrollment = options[selected]

            if st.button("Cancel Enrollment"):
                if send_data(
                    "DELETE",
                    f"/enrollments/{enrollment.get('id')}",
                ):
                    st.success("Enrollment cancelled successfully.")
                    st.rerun()
        else:
            st.info("No active enrollments to cancel.")
