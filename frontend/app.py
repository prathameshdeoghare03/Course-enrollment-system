
from pathlib import Path
from typing import Any, cast

import pandas as pd
import requests
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "https://course-enrollment-system-fgr7.onrender.com".rstrip("/")
API_TIMEOUT = 25

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "logo.png"

st.set_page_config(
    page_title="Course Enrollment System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.20);
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# API HELPERS
# =========================================================

def api_request(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
) -> tuple[bool, Any]:
    """Send a request to FastAPI and return success plus response data."""
    url = f"{API_URL}/{endpoint.lstrip('/')}"

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            json=data,
            timeout=API_TIMEOUT,
        )

        if not 200 <= response.status_code < 300:
            detail = response.text[:1000] or "No details returned."
            try:
                error_body: object = response.json()
                if isinstance(error_body, dict):
                    error_dict = cast(dict[str, Any], error_body)
                    detail = str(
                        error_dict.get("detail", error_dict)
                    )[:1000]
            except ValueError:
                pass

            return False, (
                f"HTTP {response.status_code}: {detail}"
            )

        if response.status_code == 204 or not response.content:
            return True, None

        try:
            return True, response.json()
        except ValueError:
            return True, response.text

    except requests.exceptions.Timeout:
        return False, (
            "The API request timed out. The backend may be starting "
            "or responding slowly. Try again."
        )
    except requests.exceptions.ConnectionError:
        return False, (
            "Cannot connect to the FastAPI backend. Check that the "
            "Render service is running and the API URL is correct."
        )
    except requests.exceptions.RequestException as exc:
        return False, f"Request error: {exc}"


def get_records(endpoint: str) -> list[dict[str, Any]]:
    """Fetch a list endpoint safely."""
    success, result = api_request("GET", endpoint)

    if not success:
        st.warning(f"Could not load {endpoint}: {result}")
        return []

    if not isinstance(result, list):
        st.warning(
            f"Expected a list from {endpoint}, but the API returned "
            f"{type(result).__name__}. Check the FastAPI response."
        )
        return []

    raw_items = cast(list[object], result)
    records: list[dict[str, Any]] = []
    for raw_item in raw_items:
        if isinstance(raw_item, dict):
            records.append(cast(dict[str, Any], raw_item))
    return records


def send_action(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
) -> bool:
    """Perform a mutation and display success or failure."""
    success, result = api_request(method, endpoint, data)

    if success:
        st.success("Operation completed successfully.")
        return True

    st.error(str(result))
    return False


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


def show_table(
    records: list[dict[str, Any]],
    key: str,
) -> None:
    """Display searchable records in a table."""
    if not records:
        st.info("No records found.")
        return

    df = pd.DataFrame.from_records(records)

    search = st.text_input(
        "Search records",
        key=key,
        placeholder="Search any displayed value...",
    )

    if search.strip():
        search_text = search.strip()
        searchable_rows = df.astype(str).agg(" ".join, axis=1)
        mask = searchable_rows.str.contains(
            search_text,
            case=False,
            na=False,
            regex=False,
        )
        df = df.loc[mask]

    st.caption(f"{len(df)} record(s) displayed")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    if LOGO_PATH.is_file():
        st.image(str(LOGO_PATH), width=130)
    else:
        st.title("🎓")

    st.title("Course Enrollment")
    st.caption("Online Learning Management System")
    st.divider()

    page = st.radio(
        "Navigation",
        ["Dashboard", "Courses", "Students", "Enrollments"],
    )

    st.divider()
    st.caption("Backend API")
    st.code(API_URL, language=None)

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(ttl=15, show_spinner=False)
def load_records(
    endpoint: str,
) -> tuple[list[dict[str, Any]], str | None]:
    """Cache read requests briefly to reduce unnecessary API calls."""
    success, result = api_request("GET", endpoint)

    if not success:
        return [], str(result)

    if not isinstance(result, list):
        return [], (
            f"Expected a list from {endpoint}; check the backend route."
        )

    raw_items = cast(list[object], result)
    records: list[dict[str, Any]] = []
    for raw_item in raw_items:
        if isinstance(raw_item, dict):
            records.append(cast(dict[str, Any], raw_item))
    return records, None


def refresh_data() -> None:
    load_records.clear()


courses, courses_error = load_records("/courses/")
students, students_error = load_records("/students/")
enrollments, enrollments_error = load_records("/enrollments/")

# Keep the original list helper usable after cache loading.
# The page uses the cached data above to avoid repeated requests.


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":
    header_left, header_right = st.columns([1, 5])

    with header_left:
        if LOGO_PATH.is_file():
            st.image(str(LOGO_PATH), width=100)
        else:
            st.title("🎓")

    with header_right:
        st.title("Course Enrollment System")
        st.caption("ONLINE LEARNING MANAGEMENT")
        st.write(
            "Manage courses, students, enrollments, and seat "
            "availability from one dashboard."
        )

    st.divider()

    errors = [
        message for message in (
            courses_error,
            students_error,
            enrollments_error,
        )
        if message
    ]

    if errors:
        st.warning(
            "Some dashboard data could not be loaded. "
            "Check the API status and endpoint configuration."
        )
        for message in errors:
            st.caption(message)

    total_courses = len(courses)
    total_students = len(students)

    active_enrollments = [
        enrollment for enrollment in enrollments
        if as_text(enrollment.get("status", "active")).lower()
        == "active"
    ]

    total_enrollments = len(enrollments)
    total_active = len(active_enrollments)

    total_capacity = sum(
        max(0, as_int(course.get("capacity")))
        for course in courses
    )

    available_seats = sum(
        max(0, as_int(course.get("seats_available")))
        for course in courses
    )

    occupied_seats = max(0, total_capacity - available_seats)

    utilization = (
        occupied_seats / total_capacity * 100
        if total_capacity > 0
        else 0.0
    )

    st.subheader("📊 Dashboard Overview")

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("📚 Total Courses", total_courses)
    metric2.metric("👨‍🎓 Total Students", total_students)
    metric3.metric("📝 Enrollments", total_enrollments)
    metric4.metric("💺 Available Seats", available_seats)

    st.divider()

    left, right = st.columns([2, 1])

    with left:
        st.subheader("💺 Overall Seat Utilization")
        st.progress(
            int(min(100, max(0, utilization)))
        )
        st.write(f"**{utilization:.1f}%** of capacity occupied")
        st.caption(
            "Occupied seats are estimated as total capacity "
            "minus available seats."
        )

    with right:
        st.subheader("Capacity Summary")
        st.metric("Total Capacity", f"{total_capacity:,}")
        st.metric("Estimated Occupied Seats", f"{occupied_seats:,}")
        st.metric("Active Enrollments", total_active)

    st.divider()

    st.subheader("📈 Course-wise Seat Availability")

    if courses:
        chart_rows: list[dict[str, str | int]] = []

        for course in courses:
            capacity = max(0, as_int(course.get("capacity")))
            seats = max(
                0,
                min(
                    capacity if capacity > 0 else as_int(
                        course.get("seats_available")
                    ),
                    as_int(course.get("seats_available")),
                ),
            )

            title = as_text(course.get("title")) or "Untitled course"
            course_id = course.get("id", "N/A")

            with st.expander(f"📘 {title} — ID {course_id}"):
                if capacity > 0:
                    percentage = seats / capacity * 100
                    st.progress(int(min(100, percentage)))
                    st.write(
                        f"**{seats} available** out of {capacity} seats "
                        f"({percentage:.1f}% available)"
                    )
                else:
                    st.write(f"Available seats: {seats}")
                    st.caption("Capacity is not configured.")

                st.write(
                    f"Instructor: {as_text(course.get('instructor')) or 'Not specified'}"
                )
                st.write(
                    f"Fee: {as_float(course.get('fee')):,.2f}"
                )

            chart_rows.append({
                "Course": title,
                "Available Seats": seats,
                "Occupied Seats": max(0, capacity - seats),
            })

        chart_df = pd.DataFrame.from_records(chart_rows).set_index("Course")
        st.subheader("Seat Distribution")
        st.bar_chart(
            chart_df[["Available Seats", "Occupied Seats"]]
        )
    else:
        st.info("No courses are available.")

    st.divider()
    st.subheader("📋 Course Management Overview")
    show_table(courses, "dashboard_course_search")

    st.caption("Course Enrollment System | Dashboard")


# =========================================================
# COURSES
# =========================================================

elif page == "Courses":
    st.title("📚 Course Management")

    action = st.radio(
        "Choose Action",
        ["Create", "View", "Update", "Delete"],
        horizontal=True,
        key="course_action",
    )

    if action == "Create":
        with st.form("create_course_form"):
            title = st.text_input("Course Title")
            instructor = st.text_input("Instructor")
            capacity = st.number_input(
                "Seat Capacity",
                min_value=1,
                value=30,
                step=1,
            )
            seats_available = st.number_input(
                "Seats Available",
                min_value=0,
                value=30,
                step=1,
            )
            fee = st.number_input(
                "Course Fee",
                min_value=0.0,
                value=0.0,
                step=100.0,
            )
            submitted = st.form_submit_button(
                "Create Course",
                use_container_width=True,
            )

        if submitted:
            if not title.strip():
                st.warning("Course title is required.")
            elif seats_available > capacity:
                st.warning(
                    "Available seats cannot exceed the capacity."
                )
            else:
                data: dict[str, Any] = {
                    "title": title.strip(),
                    "instructor": instructor.strip() or None,
                    "capacity": int(capacity),
                    "seats_available": int(seats_available),
                    "fee": float(fee),
                }

                if send_action("POST", "/courses/", data):
                    refresh_data()
                    st.rerun()

    elif action == "View":
        show_table(courses, "course_view_search")

    elif action == "Update":
        if not courses:
            st.info("No courses available to update.")
        else:
            options = {
                f"{c.get('id')} - {c.get('title')}": c
                for c in courses
            }
            selected = st.selectbox(
                "Select Course",
                list(options.keys()),
            )
            course = options[selected]

            current_capacity = max(
                1, as_int(course.get("capacity"), 1)
            )
            current_seats = max(
                0, as_int(course.get("seats_available"))
            )

            with st.form("update_course_form"):
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
                    value=current_capacity,
                    step=1,
                )
                seats_available = st.number_input(
                    "Seats Available",
                    min_value=0,
                    value=min(current_seats, current_capacity),
                    step=1,
                )
                fee = st.number_input(
                    "Course Fee",
                    min_value=0.0,
                    value=max(0.0, as_float(course.get("fee"))),
                    step=100.0,
                )
                submitted = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

            if submitted:
                if not title.strip():
                    st.warning("Course title is required.")
                elif seats_available > capacity:
                    st.warning(
                        "Available seats cannot exceed capacity."
                    )
                else:
                    data: dict[str, Any] = {
                        "title": title.strip(),
                        "instructor": instructor.strip() or None,
                        "capacity": int(capacity),
                        "seats_available": int(seats_available),
                        "fee": float(fee),
                    }

                    if send_action(
                        "PUT",
                        f"/courses/{course.get('id')}",
                        data,
                    ):
                        refresh_data()
                        st.rerun()

    elif action == "Delete":
        if not courses:
            st.info("No courses available to delete.")
        else:
            options = {
                f"{c.get('id')} - {c.get('title')}": c
                for c in courses
            }
            selected = st.selectbox(
                "Select Course to Delete",
                list(options.keys()),
            )
            course = options[selected]

            st.warning(
                "Deleting a course may be rejected if the backend "
                "protects courses with existing enrollments."
            )

            confirm = st.checkbox(
                "I confirm that I want to delete this course."
            )

            if st.button(
                "Delete Course",
                type="primary",
                disabled=not confirm,
            ):
                if send_action(
                    "DELETE",
                    f"/courses/{course.get('id')}",
                ):
                    refresh_data()
                    st.rerun()


# =========================================================
# STUDENTS
# =========================================================

elif page == "Students":
    st.title("👨‍🎓 Student Management")

    action = st.radio(
        "Choose Action",
        ["Register", "View", "Update", "Delete"],
        horizontal=True,
        key="student_action",
    )

    if action == "Register":
        with st.form("register_student_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            submitted = st.form_submit_button(
                "Register Student",
                use_container_width=True,
            )

        if submitted:
            if not name.strip() or not email.strip():
                st.warning("Both name and email are required.")
            elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                st.warning("Enter a valid email address.")
            else:
                data: dict[str, Any] = {
                    "name": name.strip(),
                    "email": email.strip(),
                }

                if send_action("POST", "/students/", data):
                    refresh_data()
                    st.rerun()

    elif action == "View":
        show_table(students, "student_view_search")

    elif action == "Update":
        if not students:
            st.info("No students available to update.")
        else:
            options = {
                f"{s.get('id')} - {s.get('name')}": s
                for s in students
            }
            selected = st.selectbox(
                "Select Student",
                list(options.keys()),
            )
            student = options[selected]

            with st.form("update_student_form"):
                name = st.text_input(
                    "Full Name",
                    value=as_text(student.get("name")),
                )
                email = st.text_input(
                    "Email Address",
                    value=as_text(student.get("email")),
                )
                submitted = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

            if submitted:
                if not name.strip() or not email.strip():
                    st.warning("Both name and email are required.")
                elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                    st.warning("Enter a valid email address.")
                else:
                    data: dict[str, Any] = {
                        "name": name.strip(),
                        "email": email.strip(),
                    }

                    if send_action(
                        "PUT",
                        f"/students/{student.get('id')}",
                        data,
                    ):
                        refresh_data()
                        st.rerun()

    elif action == "Delete":
        if not students:
            st.info("No students available to delete.")
        else:
            options = {
                f"{s.get('id')} - {s.get('name')}": s
                for s in students
            }
            selected = st.selectbox(
                "Select Student to Delete",
                list(options.keys()),
            )
            student = options[selected]

            confirm = st.checkbox(
                "I confirm that I want to delete this student."
            )

            if st.button(
                "Delete Student",
                type="primary",
                disabled=not confirm,
            ):
                if send_action(
                    "DELETE",
                    f"/students/{student.get('id')}",
                ):
                    refresh_data()
                    st.rerun()


# =========================================================
# ENROLLMENTS
# =========================================================

elif page == "Enrollments":
    st.title("📝 Enrollment Management")

    action = st.radio(
        "Choose Action",
        ["Enroll Student", "View", "Cancel"],
        horizontal=True,
        key="enrollment_action",
    )

    if action == "Enroll Student":
        available_courses = [
            course for course in courses
            if as_int(course.get("seats_available")) > 0
        ]

        if not students:
            st.info("Register a student before enrolling.")
        elif not available_courses:
            st.info("No courses currently have available seats.")
        else:
            student_options = {
                f"{s.get('id')} - {s.get('name')} ({s.get('email', '')})": s
                for s in students
            }

            course_options = {
                (
                    f"{c.get('id')} - {c.get('title')} "
                    f"({as_int(c.get('seats_available'))} seats left)"
                ): c
                for c in available_courses
            }

            with st.form("enroll_student_form"):
                selected_student = st.selectbox(
                    "Select Student",
                    list(student_options.keys()),
                )
                selected_course = st.selectbox(
                    "Select Course",
                    list(course_options.keys()),
                )
                submitted = st.form_submit_button(
                    "Enroll Student",
                    use_container_width=True,
                )

            if submitted:
                student = student_options[selected_student]
                course = course_options[selected_course]

                data: dict[str, Any] = {
                    "student_id": as_int(student.get("id")),
                    "course_id": as_int(course.get("id")),
                }

                # Change this endpoint if your backend defines POST /enroll.
                if send_action("POST", "/enrollments/", data):
                    refresh_data()
                    st.rerun()

    elif action == "View":
        show_table(enrollments, "enrollment_view_search")

    elif action == "Cancel":
        active_enrollments = [
            enrollment for enrollment in enrollments
            if as_text(
                enrollment.get("status", "active")
            ).lower() == "active"
        ]

        if not active_enrollments:
            st.info("No active enrollments available to cancel.")
        else:
            options = {
                (
                    f"Enrollment {e.get('id')} — "
                    f"Student {e.get('student_id')} — "
                    f"Course {e.get('course_id')}"
                ): e
                for e in active_enrollments
            }

            selected = st.selectbox(
                "Select Enrollment",
                list(options.keys()),
            )
            enrollment = options[selected]

            st.warning(
                "Cancellation should update the enrollment status "
                "and restore a seat in the backend."
            )

            confirm = st.checkbox(
                "I confirm that I want to cancel this enrollment."
            )

            if st.button(
                "Cancel Enrollment",
                type="primary",
                disabled=not confirm,
            ):
                if send_action(
                    "DELETE",
                    f"/enrollments/{enrollment.get('id')}",
                ):
                    refresh_data()
                    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()
st.caption(
    "Course Enrollment System | Streamlit Frontend | FastAPI Backend"
)
