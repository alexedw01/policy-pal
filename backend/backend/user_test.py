import json
import pytest
from backend.app import app, db, User

@pytest.fixture
def client():
    """
    Fixture for configuring the Flask application for testing.

    The application is set to testing mode and uses an in-memory SQLite database.
    The database tables are created before yielding the test client and cleaned up afterward.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_register_success(client):
    """
    Test that a user is successfully registered.

    Sends a POST request to the /api/auth/register endpoint with a valid payload.
    Asserts that the response status is 201 and the response contains an access token
    and user object with the expected fields.
    """
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post(
        "/api/auth/register",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert "user" in data
    user = data["user"]
    assert "id" in user
    assert "email" in user and user["email"] == payload["email"]
    assert "username" in user and user["username"] == payload["username"]

def test_register_missing_fields(client):
    """
    Test registration with missing fields.

    Sends a POST request to the /api/auth/register endpoint omitting the password.
    Asserts that the response status is 400 and the error message indicates missing fields.
    """
    payload = {
        "email": "test@example.com",
        "username": "testuser"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Missing required fields"

def test_register_duplicate(client):
    """
    Test registration with duplicate user data.

    Registers a user and then attempts to register the same user again.
    Asserts that the first registration succeeds with a 201 status, while the duplicate registration
    fails with a 400 status and an appropriate error message.
    """
    payload = {
        "email": "duplicate@example.com",
        "username": "duplicateuser",
        "password": "password123"
    }
    response1 = client.post("/api/auth/register", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/api/auth/register", json=payload)
    assert response2.status_code == 400
    data = response2.get_json()
    assert "error" in data
    assert data["error"] == "User with given email or username already exists"

def test_get_users(client):
    """
    Test retrieval of users.

    Initially checks that the /api/auth/users endpoint returns an empty list.
    After registering a user, asserts that the list contains one user with the expected fields.
    """
    response = client.get("/api/auth/users")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

    payload = {
        "email": "user1@example.com",
        "username": "user1",
        "password": "password1"
    }
    client.post("/api/auth/register", json=payload)
    response = client.get("/api/auth/users")
    data = response.get_json()
    assert len(data) == 1
    user = data[0]
    assert "id" in user
    assert "email" in user
    assert "username" in user

def test_login_success_with_email(client):
    """
    Test successful login using email.

    Registers a user and then logs in using the user's email.
    Asserts that the login is successful with a 200 status and that an access token
    and user details are returned.
    """
    payload = {
        "email": "login_email@example.com",
        "username": "loginuser",
        "password": "secret"
    }
    reg_response = client.post("/api/auth/register", json=payload)
    assert reg_response.status_code == 201

    login_payload = {
        "username_or_email": payload["email"],
        "password": payload["password"]
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert "user" in data
    user = data["user"]
    assert user["email"] == payload["email"]
    assert user["username"] == payload["username"]

def test_login_success_with_username(client):
    """
    Test successful login using username.

    Registers a user and then logs in using the user's username.
    Asserts that the login is successful with a 200 status and that an access token
    and user details are returned.
    """
    payload = {
        "email": "login_username@example.com",
        "username": "loginuser2",
        "password": "secret2"
    }
    reg_response = client.post("/api/auth/register", json=payload)
    assert reg_response.status_code == 201

    login_payload = {
        "username_or_email": payload["username"],
        "password": payload["password"]
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert "user" in data
    user = data["user"]
    assert user["email"] == payload["email"]
    assert user["username"] == payload["username"]

def test_login_missing_fields(client):
    """
    Test login attempt with missing fields.

    Sends a login request without a password.
    Asserts that the response status is 400 and an error message is returned.
    """
    login_payload = {
        "username_or_email": "someone@example.com"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Missing required fields"

def test_login_invalid_credentials(client):
    """
    Test login attempt with invalid credentials.

    Registers a user and attempts to log in with an incorrect password.
    Asserts that the response status is 401 and an error message is returned.
    """
    payload = {
        "email": "invalid@example.com",
        "username": "invaliduser",
        "password": "rightpassword"
    }
    client.post("/api/auth/register", json=payload)

    login_payload = {
        "username_or_email": payload["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Invalid credentials"
