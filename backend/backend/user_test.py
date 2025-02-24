import json
import pytest
from backend.app import app, db, User

@pytest.fixture
def client():
    """
    Configures the Flask application for testing using an in-memory SQLite database.
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
    Test that a user is successfully registered with all required fields.
    """
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword",
        "age": 21,
        "gender": "male",
        "ethnicity": "asian",
        "state": "california",
        "political_affiliation": "democrat"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert "user" in data
    user = data["user"]
    assert "id" in user
    assert user["email"] == payload["email"]
    assert user["username"] == payload["username"]

def test_register_missing_fields(client):
    """
    Test registration with missing required fields.
    Omits several required fields so that the endpoint returns an error.
    """
    payload = {
        "email": "missing@example.com",
        "username": "missinguser"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Missing required fields"

def test_register_duplicate(client):
    """
    Test registration with duplicate user data.
    First registration should succeed and duplicate should fail.
    """
    payload = {
        "email": "duplicate@example.com",
        "username": "duplicateuser",
        "password": "password123",
        "age": 30,
        "gender": "female",
        "ethnicity": "white",
        "state": "texas",
        "political_affiliation": "independent"
    }
    response1 = client.post("/api/auth/register", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/api/auth/register", json=payload)
    assert response2.status_code == 400
    data = response2.get_json()
    assert "error" in data
    assert data["error"] == "User with given email or username already exists"

def test_register_invalid_age(client):
    """
    Test registration with an invalid age (too low).
    Valid age must be greater than 1 and less than 100.
    """
    payload = {
        "email": "lowage@example.com",
        "username": "lowageuser",
        "password": "password",
        "age": 1,  # Invalid age
        "gender": "male",
        "ethnicity": "asian",
        "state": "california",
        "political_affiliation": "democrat"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Given age is invalid"

def test_register_invalid_gender(client):
    """
    Test registration with an invalid gender.
    """
    payload = {
        "email": "invalidgender@example.com",
        "username": "invalidgenderuser",
        "password": "password",
        "age": 25,
        "gender": "unknown",  # Invalid gender
        "ethnicity": "asian",
        "state": "california",
        "political_affiliation": "democrat"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Given gender is invalid"

def test_register_invalid_ethnicity(client):
    """
    Test registration with an invalid ethnicity.
    """
    payload = {
        "email": "invalidethnicity@example.com",
        "username": "invalidethnicityuser",
        "password": "password",
        "age": 25,
        "gender": "male",
        "ethnicity": "martian",  # Invalid ethnicity
        "state": "california",
        "political_affiliation": "democrat"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Given ethnicity is invalid"

def test_register_invalid_state(client):
    """
    Test registration with an invalid state.
    """
    payload = {
        "email": "invalidstate@example.com",
        "username": "invalidstateuser",
        "password": "password",
        "age": 25,
        "gender": "male",
        "ethnicity": "asian",
        "state": "atlantis",  # Invalid state
        "political_affiliation": "democrat"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Given state is invalid"

def test_register_invalid_political_affiliation(client):
    """
    Test registration with an invalid political affiliation.
    """
    payload = {
        "email": "invalidpol@example.com",
        "username": "invalidpoluser",
        "password": "password",
        "age": 25,
        "gender": "male",
        "ethnicity": "asian",
        "state": "california",
        "political_affiliation": "fanatic"  # Invalid political affiliation
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Given political affiliation is invalid"

def test_get_users(client):
    """
    Test retrieval of registered users.
    """
    # Initially, the users list should be empty.
    response = client.get("/api/auth/users")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

    payload = {
        "email": "user1@example.com",
        "username": "user1",
        "password": "password1",
        "age": 22,
        "gender": "female",
        "ethnicity": "white",
        "state": "florida",
        "political_affiliation": "independent"
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
    Test successful login using the user's email.
    """
    payload = {
        "email": "login_email@example.com",
        "username": "loginuser",
        "password": "secret",
        "age": 25,
        "gender": "male",
        "ethnicity": "asian",
        "state": "california",
        "political_affiliation": "democrat"
    }
    reg_response = client.post("/api/auth/register", json=payload)
    assert reg_response.status_code == 201

    login_payload = {
        "email": payload["email"],  
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
    Test successful login using the user's username.
    """
    payload = {
        "email": "login_username@example.com",
        "username": "loginuser2",
        "password": "secret2",
        "age": 26,
        "gender": "female",
        "ethnicity": "hispanic or latino",
        "state": "new york",
        "political_affiliation": "republican"
    }
    reg_response = client.post("/api/auth/register", json=payload)
    assert reg_response.status_code == 201

    login_payload = {
        "email": payload["username"], 
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
    Test login attempt with missing required fields.
    """
    login_payload = {
        "email": "someone@example.com"  
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Missing required fields"

def test_login_invalid_credentials(client):
    """
    Test login attempt with invalid credentials.
    """
    payload = {
        "email": "invalid@example.com",
        "username": "invaliduser",
        "password": "rightpassword",
        "age": 30,
        "gender": "male",
        "ethnicity": "asian",
        "state": "california",
        "political_affiliation": "democrat"
    }
    client.post("/api/auth/register", json=payload)

    login_payload = {
        "email": payload["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Invalid credentials"
