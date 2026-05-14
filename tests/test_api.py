"""
Basic API tests.
Usage: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_and_login():
    # Register
    r = client.post("/api/auth/register", json={
        "full_name": "Test Student",
        "email": "test@example.com",
        "password": "password123",
        "role": "student",
    })
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"

    # Login
    r = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_duplicate_register():
    for _ in range(2):
        client.post("/api/auth/register", json={
            "full_name": "Dup User", "email": "dup@x.com",
            "password": "pass1234", "role": "student",
        })
    r = client.post("/api/auth/register", json={
        "full_name": "Dup User", "email": "dup@x.com",
        "password": "pass1234", "role": "student",
    })
    assert r.status_code == 400


def _get_token(role="student"):
    email = f"{role}_test@test.com"
    client.post("/api/auth/register", json={
        "full_name": f"Test {role}", "email": email,
        "password": "pass1234", "role": role,
    })
    r = client.post("/api/auth/login", json={"email": email, "password": "pass1234"})
    return r.json()["access_token"]


def test_quiz_topics():
    token = _get_token("student")
    r = client.get("/api/quiz/topics", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "dental_caries" in r.json()


def test_cv_conditions():
    token = _get_token("student")
    r = client.get("/api/cv/conditions", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_my_progress():
    token = _get_token("student")
    r = client.get("/api/reports/student/my-progress", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "total_attempts" in r.json()


def test_faculty_only_endpoint():
    token = _get_token("student")
    r = client.get("/api/reports/faculty/overview", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
