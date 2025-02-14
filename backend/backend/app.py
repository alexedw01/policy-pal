import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from dotenv import load_dotenv
import click
from flask.cli import with_appcontext

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

# Define the User model with a custom table name and an increased password_hash length
class User(db.Model):
    __tablename__ = "users"  # Use "users" instead of the reserved "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Increase the length to 256 to store longer hashes
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Flask CLI command to initialize the database
@app.cli.command("init-db")
@with_appcontext
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo("Database tables created.")

# Endpoint to register a new user
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    # Validate required fields
    if not email or not username or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if a user with the same email or username already exists
    if User.query.filter(or_(User.email == email, User.username == username)).first():
        return jsonify({"error": "User with given email or username already exists"}), 400

    # Create new user and hash the password
    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

# Endpoint to get all users
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    users_list = [
        {"id": user.id, "email": user.email, "username": user.username}
        for user in users
    ]
    return jsonify(users_list), 200

# Endpoint to log in
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username_or_email = data.get("username_or_email")
    password = data.get("password")

    if not username_or_email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Try to find the user by email or username
    user = User.query.filter(
        or_(User.email == username_or_email, User.username == username_or_email)
    ).first()

    if user and user.check_password(password):
        return jsonify({"message": "Logged in successfully"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
