"""
Flask Application for User Management

This module provides a Flask application that supports user registration,
login, and retrieval of user details. It uses Flask-SQLAlchemy for database operations,
Flask CLI for command line commands, and includes secure password handling.
"""

import os
import click
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Get database configuration from environment variables
PASSWORD = os.getenv("PASSWORD")
PUBLIC_IP_ADDRESS = os.getenv("PUBLIC_IP_ADDRESS")
DBNAME = os.getenv("DBNAME")
DB_USER = os.getenv("DB_USER", "postgres")

# Build the SQLAlchemy connection URI
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{DB_USER}:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


class User(db.Model):
    """
    User model for storing user details.

    Attributes:
        id (int): Primary key for the user record.
        email (str): Unique email address of the user.
        username (str): Unique username chosen by the user.
        password_hash (str): Hashed password for security.

    Methods:
        set_password(password: str) -> None:
            Hashes the provided password and sets it to the user's password_hash.
        check_password(password: str) -> bool:
            Verifies if the provided password matches the stored password_hash.
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password: str) -> None:
        """
        Hashes and sets the user's password.

        Args:
            password (str): The plain text password to be hashed.

        Returns:
            None
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Checks if the provided password matches the stored hash.

        Args:
            password (str): The plain text password to verify.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        return check_password_hash(self.password_hash, password)


@app.after_request
def set_security_headers(response):
    """
    Set security headers for each response to protect against script injection and other attacks.

    Args:
        response (Response): The Flask response object.

    Returns:
        Response: The modified response object with security headers.
    """
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "upgrade-insecure-requests;"
    )
    return response


@app.cli.command("init-db")
@with_appcontext
def init_db() -> None:
    """
    Initialize the database by creating all tables.

    CLI Command:
        flask init-db

    Returns:
        None

    Side Effects:
        Creates database tables as defined by SQLAlchemy models.
    """
    db.create_all()
    click.echo("Database tables created.")


@app.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Endpoint: /register
    Method: POST

    Request JSON Body:
        {
            "email": str,       # User's email address.
            "username": str,    # User's desired username.
            "password": str     # User's plain text password.
        }

    Returns:
        JSON response with:
            - 201: {"message": "User created successfully"} on successful registration.
            - 400: {"error": "Missing required fields"} if any field is absent.
            - 400: {"error": "User with given email or username already exists"} if duplicate user.

    Note:
        This endpoint adheres to the Information Hiding Principle by exposing only the necessary contract
        (input fields and expected responses) while encapsulating internal logic such as password hashing.
    """
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    # Validate required fields
    if not email or not username or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Check for existing user with the same email or username
    if User.query.filter(or_(User.email == email, User.username == username)).first():
        return jsonify({"error": "User with given email or username already exists"}), 400

    # Create new user and hash the password
    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@app.route("/users", methods=["GET"])
def get_users():
    """
    Retrieve all users.

    Endpoint: /users
    Method: GET

    Returns:
        JSON list of user objects, each containing:
            - id (int)
            - email (str)
            - username (str)
        Status Code 200 on success.
    """
    users = User.query.all()
    users_list = [
        {"id": user.id, "email": user.email, "username": user.username}
        for user in users
    ]
    return jsonify(users_list), 200


@app.route("/login", methods=["POST"])
def login():
    """
    Log in a user.

    Endpoint: /login
    Method: POST

    Request JSON Body:
        {
            "username_or_email": str,   # User's email or username.
            "password": str             # User's plain text password.
        }

    Returns:
        - 200: {"message": "Logged in successfully"} if credentials are valid.
        - 400: {"error": "Missing required fields"} if any field is absent.
        - 401: {"error": "Invalid credentials"} if authentication fails.
    """
    data = request.get_json()
    username_or_email = data.get("username_or_email")
    password = data.get("password")

    if not username_or_email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Find the user by email or username
    user = User.query.filter(
        or_(User.email == username_or_email, User.username == username_or_email)
    ).first()

    if user and user.check_password(password):
        return jsonify({"message": "Logged in successfully"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.cli.command("reset-db")
@with_appcontext
def reset_db() -> None:
    """
    Reset the database by dropping all tables and recreating them.

    CLI Command:
        flask reset-db

    Returns:
        None

    Side Effects:
        Drops and recreates all database tables, effectively resetting the database.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()
    click.echo("Database reset complete.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
