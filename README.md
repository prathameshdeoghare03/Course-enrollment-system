<<<<<<< HEAD
# 🎓 Online Course Enrollment System

A web-based application developed using FastAPI, PostgreSQL, SQLAlchemy, and Streamlit to manage courses, students, and course enrollments. The project provides REST API endpoints for backend operations and a Streamlit dashboard for interacting with and viewing the system's data.

The system handles course capacity, checks seat availability, prevents duplicate enrollments, and supports enrollment cancellation while maintaining enrollment history.

## 📌 Problem Statement

Online learning platforms need an efficient way to manage courses, student records, and enrollments. Manual enrollment processes or systems without proper validation can lead to duplicate enrollments, overbooking, incorrect seat availability, and loss of enrollment history.

The objective of this project is to develop an Online Course Enrollment System that manages courses and students, validates enrollment requests, prevents duplicate enrollments, and ensures that students can enroll only when seats are available. The system also supports enrollment cancellation while maintaining enrollment history.

The application uses FastAPI for backend API development, PostgreSQL for persistent data storage, SQLAlchemy for database operations, Pydantic for data validation, and Streamlit for the frontend dashboard.

## 📌 Project Overview

The application provides REST API endpoints for managing courses, students, and enrollments. Users can interact with the system through a Streamlit dashboard, while the backend processes requests and stores data in PostgreSQL.

The project follows this workflow:

**Frontend Dashboard → HTTP Requests → FastAPI Endpoints → Pydantic Validation → SQLAlchemy CRUD Operations → PostgreSQL Database → API Response → Dashboard Display**

## 🎯 Objectives

- Create and manage course records.
- Create and manage student records.
- Enroll students in available courses.
- Prevent duplicate enrollments.
- Check course seat availability before enrollment.
- Support enrollment cancellation while retaining enrollment history.
- Store application data in PostgreSQL.
- Validate request data using Pydantic.
- Test backend endpoints using Swagger UI.
- Display course, student, enrollment, and seat information through Streamlit.

## 🛠️ Technologies Used

- **Python 3.14** – Application development
- **FastAPI** – Backend REST API development
- **Pydantic** – Request data validation
- **SQLAlchemy** – Database models and CRUD operations
- **PostgreSQL** – Relational database
- **pgAdmin** – Database management
- **Swagger UI** – API testing
- **Streamlit** – Frontend dashboard
- **Requests** – HTTP communication between frontend and backend
- **Pandas** – Data handling and tabular display

## 📂 Project Structure

```text
Course Enrollment System/
│
├── backend/
│   ├── .venv/
│   ├── routers/
│   │   ├── courses.py
│   │   ├── enrollments.py
│   │   └── students.py
│   │
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schema.py
│
├── frontend/
│   ├── .venv/
│   ├── app.py
│   └── logo.png
│
├── README.md
└── requirements.txt
```

## 🗄️ Database

The project uses PostgreSQL to store application data.

### 1. Courses Table

Stores information about available courses.

- `id` – Unique course identifier
- `title` – Course title
- `instructor` – Instructor name
- `capacity` – Total number of seats
- `seats_available` – Number of remaining seats
- `fee` – Course fee

### 2. Students Table

Stores student information.

- `id` – Unique student identifier
- `name` – Student name
- `email` – Student email address

### 3. Enrollments Table

Stores enrollment records linking students to courses. It may also include enrollment dates and status, depending on the implemented database schema.

## 🔄 Application Workflow

1. The user interacts with the Streamlit frontend.
2. The frontend sends HTTP requests using the Requests library.
3. FastAPI receives requests through the appropriate router.
4. Pydantic validates incoming request data.
5. CRUD operations process database actions using SQLAlchemy.
6. PostgreSQL stores or retrieves the requested information.
7. FastAPI returns a response to the frontend.
8. Streamlit displays the results to the user.

## ⚙️ Backend Architecture

### 1. `main.py`

Initializes the FastAPI application and includes the required routers.

### 2. `database.py`

Configures the PostgreSQL database connection and provides database access to the application.

### 3. `models.py`

Defines SQLAlchemy models representing the database tables.

### 4. `schema.py`

Defines Pydantic schemas used to validate incoming data and structure API responses.

### 5. `crud.py`

Contains database operations for creating, reading, updating, and managing records.

### 6. `routers/`

Organizes API endpoints by resource.

- `courses.py` – Course-related endpoints
- `students.py` – Student-related endpoints
- `enrollments.py` – Enrollment-related endpoints

## 🔌 API Endpoints

The API is organized into three main resources.

| Resource | Operations |
|---|---|
| Courses | Create, view, update, and manage courses |
| Students | Create, view, update, and manage student records |
| Enrollments | Enroll students, view enrollment records, and cancel enrollments |

The exact endpoint paths, HTTP methods, and request schemas are defined in the application.

### Swagger UI

FastAPI provides interactive API documentation for testing available endpoints.

**URL:** `http://127.0.0.1:8000/docs`

## 📏 Business Rules

- A student cannot enroll in the same course more than once while an active enrollment exists.
- Enrollment is allowed only when seats are available.
- Course capacity must not be exceeded.
- Cancelling an enrollment should preserve its history when supported by the implemented logic.
- Seat availability must remain consistent when enrollments are created or cancelled.
- Course deletion must respect existing enrollment history and database relationships.

## 🖥️ Frontend Dashboard

The frontend is developed using Streamlit and communicates with the FastAPI backend through HTTP requests.

The dashboard displays information such as:

- Total number of courses
- Total number of students
- Total number of enrollments
- Available seats
- Course-wise seat availability
- Course information in a table

## 🧪 Testing

The application can be tested using Swagger UI and the Streamlit dashboard.

Testing includes:

- Creating and viewing courses
- Creating and viewing students
- Enrolling students in courses
- Checking seat availability
- Testing duplicate enrollment prevention
- Cancelling enrollments
- Verifying database records
- Checking that the frontend displays the expected data

## 🚀 How to Run the Project

### 1. Install Dependencies

Open a terminal in the project directory and install the required packages:

```bash
python -m pip install -r requirements.txt
```

Make sure the packages are installed in the appropriate virtual environment.

### 2. Configure PostgreSQL

1. Start PostgreSQL.
2. Open pgAdmin.
3. Create or select your project database.
4. Configure the database connection in `backend/database.py`.
5. Ensure the required database tables exist.

**Security:** Do not upload database passwords or other secret credentials to GitHub.

### 3. Run the Backend

Open a terminal in the `backend` directory and activate its virtual environment.

Run:

```bash
python -m uvicorn main:app --reload
```

The backend will usually run at:

`http://127.0.0.1:8000`

### 4. Test the API

Open the following URL in your browser:

`http://127.0.0.1:8000/docs`

Use Swagger UI to test the available API endpoints.

### 5. Run the Frontend

Open a second terminal in the `frontend` directory and activate its virtual environment.

Run:

```bash
python -m streamlit run app.py
```

The Streamlit dashboard will usually be available at:

`http://localhost:8501`

Keep the backend running while using the frontend.

## 🧠 Key Learning Outcomes

Through this project, I practiced:

- Building REST APIs using FastAPI
- Validating data using Pydantic
- Creating SQLAlchemy database models
- Performing CRUD operations
- Connecting Python applications to PostgreSQL
- Organizing backend code using routers
- Sending HTTP requests using Requests
- Building an interactive dashboard using Streamlit
- Managing relational database records
- Implementing enrollment and seat-capacity rules
- Testing APIs through Swagger UI
- Connecting frontend and backend components

## 🔮 Future Improvements

The project can be improved by:

- Adding user authentication and role-based access.
- Implementing an admin dashboard for course management.
- Adding search and filtering for courses and students.
- Improving error messages and input validation.
- Adding automated unit and integration tests.
- Implementing database migrations.
- Improving transaction handling for concurrent enrollments.
- Deploying the application to a cloud platform.

## ⚠️ Disclaimer

This project is developed for educational purposes to practice backend development, REST APIs, database operations, and frontend-backend integration.

## 👨‍💻 Author

**Prathamesh Deoghare**

- **GitHub:** [prathameshdeoghare03](https://github.com/prathameshdeoghare03)
- **LinkedIn:** [Prathamesh Deoghare](https://www.linkedin.com/in/prathamesh-deoghare-2524632b8/)

=======
# course-enrollment-system
Course Enrollment System using FastAPI and PostgreSQL
>>>>>>> a74de32e0075da6f76eed6c33fd3ca8e0b36e440
