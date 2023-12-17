# Import FastAPI and TestClient
import os
from models import User, UserRole
from fastapi import FastAPI
from fastapi.testclient import TestClient



# os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:password@db:5432/book_db"
os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:password@localhost:5433/book_db"

# Import your app from where it's defined
from myapi import app, get_user 

# Replacing app with the module where FastAPI app is defined
# Initialize the TestClient with your app
client = TestClient(app)

testEmail = "tested12@example.com"

def mock_get_user_teacher():
    mock_user = User(id =11, name="Teacher", role = UserRole.TEACHER)
    return mock_user


def mock_get_user_student():
    mock_user = User(id=8, name="Student", role=UserRole.STUDENT)
    return mock_user

#test to see if a new user is  created 

def test_create_user():
    response = client.post("/create-user/", json={"name": "John Doe", "email": testEmail, "password": "secret", "role": "STUDENT"})
    assert response.status_code == 200
    assert response.json()["email"] == testEmail

# to check it the email doesn't already exist

def test_create_user_already_exists():
    client.post(
        "/create-user/",
        json={
            "name": "Test User",
            "email": testEmail,
            "password": "password123",
            "role": "STUDENT"
        }
    )
    response = client.post(
        "/create-user/",
        json={
            "name": "Test User",
            "email": testEmail,
            "password": "password123",
            "role": "STUDENT"
        }
    )
    assert response.status_code == 400
    assert "Email Already Exists!"



def test_get_user_found():
    response = client.get('/get-user/1')
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_create_course_success():
    # Assuming teacher_id is an existing teacher's user ID
    response = client.post("/create-course/", json={
        "title": "New Course",
        "description": "A new course description",
        "creator_id": 11
    })
    assert response.status_code == 200
    assert response.json()["creator"]["id"] == 11


def test_get_course_success():
    course_id = 8  # Assuming this course exists
    response = client.get(f"/get-course/{course_id}")
    assert response.status_code == 200
    assert "title" in response.json()


def test_get_course_not_found():
    course_id = 9999  # Assuming this course does not exist
    response = client.get(f"/get-course/{course_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


#-------------#---------------#


def test_create_lesson_success():
    # Override the get_user dependency
    app.dependency_overrides[get_user] = mock_get_user_teacher
    response = client.post("/create-lesson/", json={
        "title": "Test Lesson",
        "content": "Test Content",
        "course_id": 2  # Assuming this course exists
    })
    # Revert back to original dependency after the test
    app.dependency_overrides[get_user] = get_user
    assert response.status_code == 200
    assert "title" in response.json()

def test_create_lesson_unauthorized():
    # Override with a student mock
    app.dependency_overrides[get_user] = mock_get_user_student
    response = client.post("/create-lesson/", json={
        "title": "Test Lesson",
        "content": "Test Content",
        "course_id": 1
    })
    # Revert back to original dependency
    app.dependency_overrides[get_user] = get_user
    assert response.status_code == 403
    assert response.json()["detail"] == "Either user doesn't exist, Else Only teachers can create lessons"