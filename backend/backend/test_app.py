import pytest
from backend.app import app, db, User

@pytest.fixture
def client():
    # Configure the app for testing and override the database URI with an in-memory SQLite DB.
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def runner(client):
    return client.application.test_cli_runner()

def test_register_success(client):
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
    # Omit the password field.
    payload = {
        "email": "test@example.com",
        "username": "testuser"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_register_duplicate(client):
    payload = {
        "email": "duplicate@example.com",
        "username": "duplicateuser",
        "password": "password123"
    }
    # First registration should succeed.
    response1 = client.post("/register", json=payload)
    assert response1.status_code == 201

    # Second registration with the same email and username should fail.
    response2 = client.post("/register", json=payload)
    assert response2.status_code == 400
    data = response2.get_json()
    assert "error" in data

def test_get_users(client):
    # Initially, there should be no users.
    response = client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

    # Create a user and verify that the list is updated.
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
    # Register a new user.
    payload = {
        "email": "login_email@example.com",
        "username": "loginuser",
        "password": "secret"
    }
    client.post("/register", json=payload)

    # Login using email.
    login_payload = {
        "username_or_email": "login_email@example.com",
        "password": "secret"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Logged in successfully"

def test_login_success_with_username(client):
    # Register a new user.
    payload = {
        "email": "login_username@example.com",
        "username": "loginuser2",
        "password": "secret2"
    }
    client.post("/register", json=payload)

    # Login using username.
    login_payload = {
        "username_or_email": "loginuser2",
        "password": "secret2"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Logged in successfully"

def test_login_missing_fields(client):
    # Missing the password field.
    login_payload = {
        "username_or_email": "someone@example.com"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_login_invalid_credentials(client):
    # Register a user.
    payload = {
        "email": "invalid@example.com",
        "username": "invaliduser",
        "password": "rightpassword"
    }
    client.post("/register", json=payload)

    # Try logging in with the wrong password.
    login_payload = {
        "username_or_email": "invalid@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data

def test_init_db_cli(runner, client):
    # The CLI command should output a confirmation message.
    result = runner.invoke(args=["init-db"])
    assert "Database tables created." in result.output

def test_reset_db_cli(client, runner):
    # Insert a dummy user directly using SQLAlchemy.
    with app.app_context():
        user = User(email="dummy@example.com", username="dummy", password_hash="dummyhash")
        db.session.add(user)
        db.session.commit()
        # Verify that the user was added.
        assert User.query.count() == 1

    # Invoke the CLI command to reset the database.
    result = runner.invoke(args=["reset-db"])
    assert "Database reset complete." in result.output

    # Verify that the database has been cleared.
    with app.app_context():
        assert User.query.count() == 0
