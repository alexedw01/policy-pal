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

@pytest.fixture
def runner(client):
    """
    Fixture for obtaining a test CLI runner for the Flask application.
    """
    return client.application.test_cli_runner()

def test_register_success(client):
    """
    Test that a user is successfully registered.

    Sends a POST request to the /register endpoint with a valid payload.
    Asserts that the response status is 201 and the response message confirms user creation.
    """
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "User created successfully"

def test_register_missing_fields(client):
    """
    Test registration with missing fields.

    Sends a POST request to the /register endpoint omitting the password.
    Asserts that the response status is 400 and an error is returned.
    """
    payload = {
        "email": "test@example.com",
        "username": "testuser"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_register_duplicate(client):
    """
    Test registration with duplicate user data.

    Registers a user and then attempts to register the same user again.
    Asserts that the first registration succeeds with a 201 status, while the duplicate registration fails with a 400 status.
    """
    payload = {
        "email": "duplicate@example.com",
        "username": "duplicateuser",
        "password": "password123"
    }
    response1 = client.post("/register", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/register", json=payload)
    assert response2.status_code == 400
    data = response2.get_json()
    assert "error" in data

def test_get_users(client):
    """
    Test retrieval of users.

    Initially checks that the /users endpoint returns an empty list.
    After registering a user, asserts that the list contains one user with the expected fields.
    """
    response = client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

    payload = {
        "email": "user1@example.com",
        "username": "user1",
        "password": "password1"
    }
    client.post("/register", json=payload)
    response = client.get("/users")
    data = response.get_json()
    assert len(data) == 1
    user = data[0]
    assert "id" in user and "email" in user and "username" in user

def test_login_success_with_email(client):
    """
    Test successful login using email.

    Registers a user and then logs in using the user's email.
    Asserts that the login is successful with a 200 status and the appropriate message.
    """
    payload = {
        "email": "login_email@example.com",
        "username": "loginuser",
        "password": "secret"
    }
    client.post("/register", json=payload)

    login_payload = {
        "username_or_email": "login_email@example.com",
        "password": "secret"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Logged in successfully"

def test_login_success_with_username(client):
    """
    Test successful login using username.

    Registers a user and then logs in using the user's username.
    Asserts that the login is successful with a 200 status and the appropriate message.
    """
    payload = {
        "email": "login_username@example.com",
        "username": "loginuser2",
        "password": "secret2"
    }
    client.post("/register", json=payload)

    login_payload = {
        "username_or_email": "loginuser2",
        "password": "secret2"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Logged in successfully"

def test_login_missing_fields(client):
    """
    Test login attempt with missing fields.

    Sends a login request without a password.
    Asserts that the response status is 400 and an error message is returned.
    """
    login_payload = {
        "username_or_email": "someone@example.com"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

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
    client.post("/register", json=payload)

    login_payload = {
        "username_or_email": "invalid@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data

def test_init_db_cli(runner, client):
    """
    Test the CLI command for initializing the database.

    Invokes the 'init-db' CLI command and asserts that the output confirms table creation.
    """
    result = runner.invoke(args=["init-db"])
    assert "Database tables created." in result.output

def test_reset_db_cli(client, runner):
    """
    Test the CLI command for resetting the database.

    Inserts a dummy user, verifies the insertion, invokes the 'reset-db' CLI command,
    and then verifies that the user count is zero.
    """
    with app.app_context():
        user = User(email="dummy@example.com", username="dummy", password_hash="dummyhash")
        db.session.add(user)
        db.session.commit()
        assert User.query.count() == 1

    result = runner.invoke(args=["reset-db"])
    assert "Database reset complete." in result.output

    with app.app_context():
        assert User.query.count() == 0
