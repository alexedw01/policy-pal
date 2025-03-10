"""
Flask Application for Backend Management

This module provides a Flask application that supports user registration,
login, bill storage, and scraping/updating congressional bill details.
It uses Flask-SQLAlchemy for database operations, Flask CLI for command line commands,
and includes secure password handling.
"""

import os
import json
import time
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
import requests
import openai
import click

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy  
from sqlalchemy import or_, text
from sqlalchemy.ext.mutable import MutableDict
from flask_cors import CORS
from flask.cli import with_appcontext
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.security import generate_password_hash, check_password_hash

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------------------------------------------------------------
# Application and Configuration
# ------------------------------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS", "PUT"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Authorization"]
    }
})

load_dotenv()

# Database configuration from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
PASSWORD = os.getenv("PASSWORD")
PUBLIC_IP_ADDRESS = os.getenv("PUBLIC_IP_ADDRESS")
DBNAME = os.getenv("DBNAME")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{DB_USER}:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------------------------------------------------------------------------
# Data Model Entities
# ------------------------------------------------------------------------------
class User(db.Model):
    """
    User model for storing user details.

    Attributes:
        id (int): Primary key for the user record.
        email (str): Unique email address of the user.
        username (str): Unique username chosen by the user.
        password_hash (str): Hashed password for security.
        age (int): Age of the user.
        gender (str): Gender of the user (e.g., Male, Female, Non-binary, Other).
        ethnicity (str): Ethnic group the user belongs to (e.g. Hispanic or Latino, white, asian)
        state (str): state the user lives in. 
        political_affiliation (str): Political leaning (e.g., Democrat, Republican, Independent).
        voted_bills (JSON): A dictionary storing bill IDs as keys and the corresponding vote value as values.
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(50), nullable=True)  
    ethnicity = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    political_affiliation = db.Column(db.String(50), nullable=True)  
    
    voted_bills = db.Column(MutableDict.as_mutable(db.JSON), default=dict, nullable=False)
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)


class Bill(db.Model):
    """
    Bill model for storing congressional bill details.

    Attributes:
        id (int): Primary key for the bill record.
        congress (int): The Congress number that the bill belongs to.
        bill_type (str): The type of the bill (e.g., "H.R.", "S.").
        bill_number (str): The specific bill number.
        title (str): The title of the bill.
        latest_action_date (datetime): The date of the most recent action on the bill.
        origin_chamber (str): The chamber where the bill originated (e.g., "House", "Senate").
        sponsor (str): The name of the bill's sponsor.
        latest_action (dict): A JSON object storing details about the bill's latest action.
        update_date (datetime): The date when the bill was last updated.
        url (str): The URL linking to the bill's detailed information.
        text_preview (str): A preview snippet of the bill's text.
        full_text (str): The full text of the bill.
        ai_summary (str): An AI-generated summary of the bill.
        vote_count (int): A counter to identify bills with the most activity.
        created_at (datetime): The timestamp when the bill record was created.
        updated_at (datetime): The timestamp when the bill record was last updated.
    """
    __tablename__ = "bills"
    id = db.Column(db.Integer, primary_key=True)
    congress = db.Column(db.Integer, nullable=False)
    bill_type = db.Column(db.String(20), nullable=False)
    bill_number = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    latest_action_date = db.Column(db.DateTime, nullable=False)
    origin_chamber = db.Column(db.String(50))
    sponsor = db.Column(db.String(100))
    latest_action = db.Column(db.JSON)
    update_date = db.Column(db.DateTime, nullable=False)
    url = db.Column(db.String(512), nullable=False)
    text_preview = db.Column(db.Text)
    full_text = db.Column(db.Text)
    ai_summary = db.Column(db.Text)
    vote_count = db.Column(db.Integer, nullable=False, default=0)
    upvote_count = db.Column(db.Integer, nullable=False, default=0) 
    downvote_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

class BillSearchEntry(db.Model):
    __tablename__ = "bill_search_entries"
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), unique=True, nullable=False)
    combined_text = db.Column(db.Text, nullable=False)

def build_bill_search_entries():
    bills = Bill.query.all()
    for bill in bills:
        parts = []
        if bill.title:
            parts.append(bill.title)
        if bill.ai_summary:
            parts.append(bill.ai_summary)
        if bill.full_text:
            parts.append(bill.full_text)
        # Combine the three fields into one document.
        combined_text = " ".join(parts)
        
        entry = BillSearchEntry.query.filter_by(bill_id=bill.id).first()
        if not entry:
            entry = BillSearchEntry(bill_id=bill.id, combined_text=combined_text)
            db.session.add(entry)
        else:
            entry.combined_text = combined_text
    db.session.commit()


def default_demographics():
    return {
        "upvote": {
            "age_distribution": {"under_18": 0, "18_to_30": 0, "30_to_60": 0, "60_plus": 0},
            "gender_distribution": {"male": 0, "female": 0, "non-binary": 0, "transgender": 0, "other": 0},
            "ethnicity_distribution": {
                "hispanic or latino": 0, "white": 0, "black or african american": 0, "asian": 0,
                "native hawaiian or other pacific islander": 0, "american indian or alaska native": 0, "other": 0
            },
            "state_distribution": {
                "al": 0, "ak": 0, "az": 0, "ar": 0, "ca": 0,
                "co": 0, "ct": 0, "de": 0, "fl": 0, "ga": 0,
                "hi": 0, "id": 0, "il": 0, "in": 0, "ia": 0,
                "ks": 0, "ky": 0, "la": 0, "me": 0, "md": 0,
                "ma": 0, "mi": 0, "mn": 0, "ms": 0, "mo": 0,
                "mt": 0, "ne": 0, "nv": 0, "nh": 0, "nj": 0,
                "nm": 0, "ny": 0, "nc": 0, "nd": 0, "oh": 0,
                "ok": 0, "or": 0, "pa": 0, "ri": 0, "sc": 0,
                "sd": 0, "tn": 0, "tx": 0, "ut": 0, "vt": 0,
                "va": 0, "wa": 0, "wv": 0, "wi": 0, "wy": 0,
                "other": 0
            },
            "political_affiliation_distribution": {
                "democrat": 0, "republican": 0, "independent": 0, "libertarian": 0, "green": 0,
                "conservative": 0, "progressive": 0, "moderate": 0, "socialist": 0, "communist": 0, "other": 0
            }
        },
        "downvote": {
            "age_distribution": {"under_18": 0, "18_to_30": 0, "30_to_60": 0, "60_plus": 0},
            "gender_distribution": {"male": 0, "female": 0, "non-binary": 0, "transgender": 0, "other": 0},
            "ethnicity_distribution": {
                "hispanic or latino": 0, "white": 0, "black or african american": 0, "asian": 0,
                "native hawaiian or other pacific islander": 0, "american indian or alaska native": 0, "other": 0
            },
            "state_distribution": {
                "al": 0, "ak": 0, "az": 0, "ar": 0, "ca": 0,
                "co": 0, "ct": 0, "de": 0, "fl": 0, "ga": 0,
                "hi": 0, "id": 0, "il": 0, "in": 0, "ia": 0,
                "ks": 0, "ky": 0, "la": 0, "me": 0, "md": 0,
                "ma": 0, "mi": 0, "mn": 0, "ms": 0, "mo": 0,
                "mt": 0, "ne": 0, "nv": 0, "nh": 0, "nj": 0,
                "nm": 0, "ny": 0, "nc": 0, "nd": 0, "oh": 0,
                "ok": 0, "or": 0, "pa": 0, "ri": 0, "sc": 0,
                "sd": 0, "tn": 0, "tx": 0, "ut": 0, "vt": 0,
                "va": 0, "wa": 0, "wv": 0, "wi": 0, "wy": 0,
                "other": 0
            },
            "political_affiliation_distribution": {
                "democrat": 0, "republican": 0, "independent": 0, "libertarian": 0, "green": 0,
                "conservative": 0, "progressive": 0, "moderate": 0, "socialist": 0, "communist": 0, "other": 0
            }
        }
    }

class Vote(db.Model):
    """
    Association model that stores a vote cast by a user on a bill.

    Attributes:
        bill_id (int): Foreign key referencing the Bill being voted on.
        vote_status (str): The vote status (e.g., 'yes', 'no', 'abstain').
    """
    __tablename__ = "votes"
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), primary_key=True)
    demographics = db.Column(MutableDict.as_mutable(db.JSON), nullable=False, default=default_demographics)

class ScrapeTracking(db.Model):
    """
    Model to track the current offset for scheduled batch scrapes.

    Attributes:
        id (int): Primary key for the tracking record.
        type (str): Type of tracking record (e.g., "offset").
        offset (int): Current offset value for batch scraping.
    """
    __tablename__ = "scrape_tracking"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), unique=True, nullable=False)
    offset = db.Column(db.Integer, default=0)
    
# ------------------------------------------------------------------------------
# Scraper Class
# ------------------------------------------------------------------------------
CONGRESS_API_KEY = os.getenv("CONGRESS_API_KEY")
API_RATE_LIMIT = float(os.getenv("API_RATE_LIMIT", "2"))
CONGRESS_API_BASE = os.getenv("CONGRESS_API_BASE", "https://api.congress.gov/v3")

#credit to akash for developing this
class CongressionalScraper:
    """
    A class responsible for scraping congressional bill data from an external API.

    This class handles rate limiting for API requests and provides methods to:
      - Fetch detailed bill information from a given URL.
      - Retrieve a text preview or the full text of a bill.
      - Process bill data by checking for existing records in the database and inserting or updating them.
      - Perform batch scraping and daily updates.

    Attributes:
        headers (dict): Headers to use for API requests, including the API key.
        last_request_time (float): Timestamp of the last API request, used for rate limiting.
    """
    def __init__(self):
        """Initialize the CongressionalScraper with API headers and rate limiting parameters."""
        self.headers = {"X-API-Key": CONGRESS_API_KEY}
        self.last_request_time = 0

    def _rate_limit(self) -> None:
        """
        Implement rate limiting to ensure API requests adhere to the allowed rate.

        This method calculates the time elapsed since the last request and pauses if needed.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        wait_time = 1 / API_RATE_LIMIT
        if time_since_last_request < wait_time:
            time.sleep(wait_time - time_since_last_request)
        self.last_request_time = time.time()

    def get_bill_details(self, url: str) -> dict:
        """
        Fetch detailed bill information from the given URL.

        Args:
            url (str): The URL from which to fetch the bill details.
        Returns:
            dict: A dictionary containing detailed bill information, or an empty dict on failure.
        """
        self._rate_limit()
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("bill", {})
            app.logger.error(f"Error fetching bill details: Status {response.status_code}")
        except Exception as e:
            app.logger.error(f"Exception fetching bill details: {e}")
        return {}

    def get_bill_text(self, congress: int, bill_type: str, bill_number: str, full_text: bool = False) -> str:
        """
        Fetch the bill text from the external API.

        Args:
            congress (int): The Congress number.
            bill_type (str): The type of the bill (e.g., 'H.R.', 'S.').
            bill_number (str): The bill number.
            full_text (bool): If True, return the full text; otherwise, return a preview.
        Returns:
            str: The bill text (either full or a preview), or an empty string on failure.
        """
        self._rate_limit()
        texts_url = f"{CONGRESS_API_BASE}/bill/{congress}/{bill_type.lower()}/{bill_number}/text"
        try:
            response = requests.get(texts_url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                text_versions = data.get("textVersions", [])
                if text_versions:
                    latest_version = text_versions[0]
                    formats = latest_version.get("formats", [])
                    htm_format = next((f for f in formats if f.get("type") == "Formatted Text"), None)
                    if htm_format:
                        htm_url = htm_format.get("url")
                        app.logger.info(f"Fetching HTML from: {htm_url}")
                        self._rate_limit()
                        htm_response = requests.get(htm_url)
                        if htm_response.status_code == 200:
                            soup = BeautifulSoup(htm_response.text, 'html.parser')
                            content = soup.find('pre')
                            if content:
                                text = content.get_text(separator=' ', strip=True)
                                if full_text:
                                    return text
                                return text[:1000] + "..." if len(text) > 1000 else text
                            else:
                                app.logger.error("No <pre> tag found in HTML content.")
                        else:
                            app.logger.error(f"Failed to fetch HTML content: {htm_response.status_code}")
                    else:
                        app.logger.error("No HTML format found for bill text.")
                return ""
            else:
                app.logger.error(f"Error fetching bill texts: Status {response.status_code}. Response: {response.text}")
                return ""
        except Exception as e:
            app.logger.error(f"Exception fetching bill text: {e}")
            return ""

    def process_bill(self, bill_data: dict) -> bool:
        """
        Process a single bill by fetching additional details and inserting or updating it in the database.

        Args:
            bill_data (dict): Raw bill data obtained from the external source.
        Returns:
            bool: True if a new bill was inserted; False if an existing bill was updated or on error.
        """
        try:
            congress = bill_data["congress"]
            bill_type = bill_data["type"]
            bill_number = bill_data["number"]
            app.logger.info(f"Processing bill {bill_type}{bill_number}")

            detailed_bill = self.get_bill_details(bill_data.get("url", ""))
            if not detailed_bill:
                detailed_bill = bill_data

            # Check if the bill already exists in the database.
            existing_bill = Bill.query.filter_by(
                congress=congress, bill_type=bill_type, bill_number=bill_number
            ).first()

            action_date = (
                detailed_bill.get("latestAction", {}).get("actionDate")
                or bill_data.get("latestAction", {}).get("actionDate")
                or bill_data.get("updateDate")
            )
            try:
                latest_action_date = datetime.strptime(action_date, "%Y-%m-%d") if action_date else datetime.now(timezone.utc)
            except ValueError:
                latest_action_date = datetime.now(timezone.utc)

            bill_text = self.get_bill_text(congress, bill_type, bill_number)
            full_text = self.get_bill_text(congress, bill_type, bill_number, full_text=True)
            ai_summary = None
            if bill_text:
                if existing_bill and existing_bill.ai_summary:
                    ai_summary = existing_bill.ai_summary
                else:
                    try:
                        ai_summary_response = openai.ChatCompletion.create(
                            model="gpt-4o",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a professional congressional analyst. Summarize the following bill text concisely and objectively in 6-8 sentences."
                                },
                                {"role": "user", "content": bill_text}
                            ],
                            max_tokens=300
                        )
                        ai_summary = ai_summary_response.choices[0].message.content
                        app.logger.info(f"Generated AI summary for {bill_type}{bill_number}")
                    except Exception as e:
                        app.logger.error(f"Error generating AI summary: {e}")

            congress_url = f"https://www.congress.gov/bill/{congress}th-congress/{bill_type.lower()}/{bill_number}"
            try:
                update_date = datetime.strptime(bill_data["updateDate"], "%Y-%m-%d")
            except (KeyError, ValueError):
                update_date = datetime.now(timezone.utc)

            if existing_bill:
                existing_bill.title = detailed_bill.get("title", bill_data.get("title", ""))
                existing_bill.latest_action = detailed_bill.get("latestAction", bill_data.get("latestAction", {}))
                existing_bill.update_date = update_date
                existing_bill.text_preview = bill_text
                if not existing_bill.ai_summary:
                    existing_bill.ai_summary = ai_summary
                existing_bill.updated_at = datetime.now(timezone.utc)
                db.session.commit()
                app.logger.info(f"Updated existing bill {bill_type}{bill_number}")
                return False

            new_bill = Bill(
                congress=congress,
                bill_type=bill_type,
                bill_number=bill_number,
                title=detailed_bill.get("title", bill_data.get("title", "")),
                latest_action_date=latest_action_date,
                origin_chamber=bill_data.get("originChamber", ""),
                sponsor=detailed_bill.get("sponsor", {}).get("name", "Unknown"),
                latest_action=detailed_bill.get("latestAction", bill_data.get("latestAction", {})),
                update_date=update_date,
                url=congress_url,
                text_preview=bill_text,
                full_text=full_text,
                ai_summary=ai_summary,
                vote_count=0,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(new_bill)
            db.session.commit()
            app.logger.info(f"Successfully inserted bill {bill_type}{bill_number}")
            return True

        except Exception as e:
            app.logger.error(f"Error processing bill: {e}")
            app.logger.error("Bill data: " + json.dumps(bill_data, indent=2))
            return False


    def batch_scrape(self, congress: int, offset: int = 0, limit: int = 20) -> tuple:
        """
        Perform batch scraping of bills from the external API.

        Args:
            congress (int): The Congress number to scrape.
            offset (int, optional): Pagination offset; defaults to 0.
            limit (int, optional): Number of bills to process in one batch; defaults to 20.
        Returns:
            tuple: A tuple containing:
                - processed_count (int): Number of new bills processed.
                - batch_count (int): Number of bills fetched in the current batch.
                - total_count (int): Total available count of bills from the API.
        """
        url = f"{CONGRESS_API_BASE}/bill/{congress}"
        params = {
            "offset": offset,
            "limit": limit,
            "format": "json"
        }
        try:
            self._rate_limit()
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                bills = data.get("bills", [])
                processed_count = 0
                for bill in bills:
                    if self.process_bill(bill):
                        processed_count += 1
                total_count = data.get("pagination", {}).get("count", 0)
                return processed_count, len(bills), total_count
            else:
                app.logger.error(f"Error in batch scrape: Status {response.status_code}")
                return 0, 0, 0
        except Exception as e:
            app.logger.error(f"Exception in batch scrape: {e}")
            return 0, 0, 0

    def daily_update(self) -> int:
        """
        Perform a daily update of new and modified bills from the external API.

        Returns:
            int: The number of bills processed during the daily update.
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        current_congress = 118  # Update this value as needed
        url = f"{CONGRESS_API_BASE}/bill/{current_congress}"
        params = {
            "fromDateTime": f"{yesterday}T00:00:00Z",
            "format": "json"
        }
        try:
            self._rate_limit()
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                bills = data.get("bills", [])
                processed_count = 0
                for bill in bills:
                    if self.process_bill(bill):
                        processed_count += 1
                return processed_count
            else:
                app.logger.error(f"Error in daily update: Status {response.status_code}")
                return 0
        except Exception as e:
            app.logger.error(f"Exception in daily update: {e}")
            return 0

# ------------------------------------------------------------------------------
# Scheduled Tasks Helper Functions
# ------------------------------------------------------------------------------

#credit to akash for developing this
def scheduled_update():
    """
    Scheduled task function to perform a daily update of bills.

    This function is designed to be run on a daily schedule. It initializes
    the CongressionalScraper and calls the daily_update method, logging the number
    of bills processed.
    """
    with app.app_context():
        scraper = CongressionalScraper()
        processed = scraper.daily_update()
        app.logger.info(f"Scheduled update completed: processed {processed} bills")

def scheduled_batch_scrape():
    """
    Scheduled task function to perform batch scraping of bills.

    This function is designed to be run on a minute-by-minute schedule to
    incrementally scrape new bills. It uses the ScrapeTracking model to maintain
    the current offset and updates the offset after each batch.
    """
    with app.app_context():
        scraper = CongressionalScraper()
        tracking = ScrapeTracking.query.filter_by(type="offset").first()
        if tracking is None:
            tracking = ScrapeTracking(type="offset", offset=0)
            db.session.add(tracking)
            db.session.commit()
        current_offset = tracking.offset

        processed, batch_count, available = scraper.batch_scrape(congress=118, offset=current_offset, limit=3)
        new_offset = current_offset + 3
        tracking.offset = new_offset
        db.session.commit()
        app.logger.info(f"Scheduled batch completed: processed {processed} bills. Next offset: {new_offset}")

# ------------------------------------------------------------------------------
# Security Headers (optional)
# ------------------------------------------------------------------------------
# Uncomment the following lines to enable security headers.
# @app.after_request
# def set_security_headers(response):
#     """
#     Set security headers for each response to mitigate risks such as XSS and clickjacking.
#
#     Args:
#         response: The Flask response object.
#     Returns:
#         The response object with additional security headers.
#     """
#     response.headers['Content-Security-Policy'] = (
#         "default-src 'self'; "
#         "script-src 'self'; "
#         "style-src 'self'; "
#         "img-src 'self' data:; "
#         "font-src 'self'; "
#         "connect-src 'self'; "
#         "frame-ancestors 'none'; "
#         "object-src 'none'; "
#         "base-uri 'self'; "
#         "form-action 'self'; "
#         "upgrade-insecure-requests;"
#     )
#     return response

# ------------------------------------------------------------------------------
# CLI Commands for Initialization and Reset
# ------------------------------------------------------------------------------
@app.cli.command("init-db")
@with_appcontext
def init_db() -> None:
    """
    Initialize the database by creating all necessary tables.

    This command creates all required database tables and confirms the creation via a CLI message.
    """
    db.create_all()
    click.echo("Database tables created.")

@app.cli.command("scrape-bills")
@click.option("--congress", default=118, help="Congress number to scrape")
@click.option("--offset", default=0, help="Starting offset")
@click.option("--limit", default=20, help="Number of bills to fetch")
@with_appcontext
def scrape_bills(congress: int, offset: int, limit: int) -> None:
    """
    Scrape bills from the specified Congress session.

    This command performs a batch scrape of legislative bills using the provided parameters,
    and then updates the BillSearchEntry records used for TF–IDF search.
    
    :param congress: Congress number to scrape (default is 118).
    :param offset: Starting offset for the scraping (default is 0).
    :param limit: Number of bills to fetch (default is 20).
    """
    scraper = CongressionalScraper()
    processed, total, available = scraper.batch_scrape(congress=congress, offset=offset, limit=limit)
    click.echo(f"Scraping complete: Processed {processed} new bills out of {total} fetched bills.")
    click.echo(f"Total bills available: {available}")

    click.echo("Updating BillSearchEntry records for search...")
    build_bill_search_entries()
    click.echo("BillSearchEntry records updated.")

@app.cli.command("schedule-updates")
@with_appcontext
def init_scheduler() -> None:
    """
    Start the background scheduler for periodic scraping tasks.

    This command initializes and starts a BackgroundScheduler that schedules:
    - A batch scraping task to run every minute.
    - A daily update task to run every 24 hours.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scheduled_batch_scrape, trigger="interval", minutes=1)
    scheduler.add_job(func=scheduled_update, trigger="interval", hours=24)
    scheduler.start()
    click.echo("Scheduler started with daily and batch scraping tasks.")

@app.cli.command("reset-db")
@with_appcontext
def reset_db() -> None:
    """
    Reset the database by dropping and recreating all tables.
    
    This command drops the public schema (with CASCADE) and then recreates it, 
    ensuring that all dependent objects are removed.
    """
    # Drop the entire public schema (with cascade) and then recreate it.
    db.session.execute(text("DROP SCHEMA public CASCADE;"))
    db.session.execute(text("CREATE SCHEMA public;"))
    db.session.commit()

    # Create all tables from the models.
    db.create_all()
    db.session.commit()
    
    click.echo("Database reset complete.")
# ------------------------------------------------------------------------------
# User API Endpoints
# ------------------------------------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    
    try:
        age = int(data.get("age"))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid age format"}), 400 

    gender = data.get("gender")
    ethnicity = data.get("ethnicity")
    state = data.get("state")
    political_affiliation = data.get("political_affiliation")

    if not email or not username or not password or not age or not gender or not state or not political_affiliation:
        return jsonify({"error": "Missing required fields"}), 400
    
    if User.query.filter(or_(User.email == email, User.username == username)).first():
        return jsonify({"error": "User with given email or username already exists"}), 400

    if not (1 < age < 100):
        return jsonify({"error": "Given age is invalid"}), 400
    
    acceptable_genders = ["male", "female", "non-binary", "transgender", "other"]
    if gender.lower() not in acceptable_genders:
        return jsonify({"error": "Given gender is invalid"}), 400

    acceptable_ethnicities = ["hispanic or latino", "white", "black or african american", "asian", 
                            "native hawaiian or other pacific islander", "american indian or alaska native", "other"]

    if ethnicity.lower() not in acceptable_ethnicities:
        return jsonify({"error": "Given ethnicity is invalid"}), 400

    acceptable_states = {
        "alabama": "al", "alaska": "ak", "arizona": "az", "arkansas": "ar", "california": "ca",
        "colorado": "co", "connecticut": "ct", "delaware": "de", "florida": "fl", "georgia": "ga",
        "hawaii": "hi", "idaho": "id", "illinois": "il", "indiana": "in", "iowa": "ia",
        "kansas": "ks", "kentucky": "ky", "louisiana": "la", "maine": "me", "maryland": "md",
        "massachusetts": "ma", "michigan": "mi", "minnesota": "mn", "mississippi": "ms",
        "missouri": "mo", "montana": "mt", "nebraska": "ne", "nevada": "nv", "new hampshire": "nh",
        "new jersey": "nj", "new mexico": "nm", "new york": "ny", "north carolina": "nc",
        "north dakota": "nd", "ohio": "oh", "oklahoma": "ok", "oregon": "or", "pennsylvania": "pa",
        "rhode island": "ri", "south carolina": "sc", "south dakota": "sd", "tennessee": "tn",
        "texas": "tx", "utah": "ut", "vermont": "vt", "virginia": "va", "washington": "wa",
        "west virginia": "wv", "wisconsin": "wi", "wyoming": "wy", "other": "other"
    }

    state = state.lower()
    if state in acceptable_states.keys():
        state = acceptable_states[state]
    elif state not in acceptable_states.values():
        return jsonify({"error": "Given state is invalid"}), 400
    
    acceptable_political_affiliations = [
        "libertarian", "conservative", "progressive", "moderate", 
        "socialist", "communist", "other"
    ]
    
    if political_affiliation.lower() not in acceptable_political_affiliations:
        return jsonify({"error": "Given political affiliation is invalid"}), 400

    user = User(email=email, username=username, age=age, gender=gender.lower(), 
                ethnicity=ethnicity.lower(), state=state.lower(), 
                political_affiliation=political_affiliation.lower(),
                voted_bills={})

    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
    return jsonify({
        "message": "User created successfully",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username
        }
    }), 201

@app.route("/api/auth/users", methods=["GET"])
def get_users():
    """
    API endpoint to retrieve all registered users.

    Returns:
        A JSON list of users, where each user includes the id, email, and username.
    """
    users = User.query.all()
    users_list = [{"id": user.id, "email": user.email, "username": user.username} for user in users]
    return jsonify(users_list), 200

@app.route("/api/auth/login", methods=["POST"])
def login():
    """
    API endpoint for user login.

    Expects a JSON payload with 'username_or_email' and 'password'.
    Returns an access token and user details if credentials are valid.
    """
    data = request.get_json()
    username_or_email = data.get("email")
    password = data.get("password")

    if not username_or_email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter(
        or_(User.email == username_or_email, User.username == username_or_email)
    ).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
        return jsonify({
            "message": "Logged in successfully",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# ------------------------------------------------------------------------------
# Helper Function for Serialization
# ------------------------------------------------------------------------------
#credit to akash for developing this
def serialize_bill(bill):
    """
    Helper function to serialize a Bill object for JSON responses.

    Converts datetime fields to ISO 8601 strings.

    Args:
        bill (Bill): A Bill model instance.

    Returns:
        dict: A dictionary representation of the bill.
    """
    return {
        "_id": str(bill.id),
        "congress": bill.congress,
        "bill_type": bill.bill_type,
        "bill_number": bill.bill_number,
        "title": bill.title,
        "latest_action_date": bill.latest_action_date.isoformat() if bill.latest_action_date else None,
        "origin_chamber": bill.origin_chamber,
        "sponsor": bill.sponsor,
        "latest_action": bill.latest_action,
        "update_date": bill.update_date.isoformat() if bill.update_date else None,
        "url": bill.url,
        "text_preview": bill.text_preview,
        "full_text": bill.full_text,
        "ai_summary": bill.ai_summary,
        "vote_count": bill.vote_count if hasattr(bill, 'vote_count') else 0,
        "upvote_count": bill.upvote_count if hasattr(bill, 'upvote_count') else 0,
        "downvote_count": bill.downvote_count if hasattr(bill, 'downvote_count') else 0,
        "created_at": bill.created_at.isoformat() if bill.created_at else None,
        "updated_at": bill.updated_at.isoformat() if bill.updated_at else None
    }

# ------------------------------------------------------------------------------
# Bill API Endpoints
# ------------------------------------------------------------------------------
@app.route("/api/bills", methods=["GET"])
def get_bills():
    """
    API endpoint to retrieve bills with pagination, sorting, and optional filtering by chamber.

    Query Parameters:
        page (int): The page number (default: 1).
        per_page (int): The number of bills per page (default: 20).
        sort (str): The column to sort by (default: "created_at").
        sort_dir (int): Sort direction; 1 for ascending, -1 for descending (default: -1).
        chamber (str): The chamber to filter bills by (e.g., "House", "Senate", or "all").

    Returns:
        JSON response containing the serialized list of bills and pagination metadata.
    """
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        sort_by = request.args.get("sort", "created_at")
        sort_dir = int(request.args.get("sort_dir", -1))
        chamber = request.args.get("chamber", None)

        query = Bill.query
        if chamber and chamber.lower() != "all":
            query = query.filter(Bill.origin_chamber == chamber)

        sort_column = getattr(Bill, sort_by, Bill.created_at)
        sort_column = sort_column.desc() if sort_dir == -1 else sort_column.asc()

        pagination = query.order_by(sort_column).paginate(page=page, per_page=per_page, error_out=False)
        bills = pagination.items

        return jsonify({
            "bills": [serialize_bill(bill) for bill in bills],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        })
    except Exception as e:
        app.logger.error(f"Error fetching bills: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/bills/trending", methods=["GET"])
def get_trending_bills():
    """
    API endpoint to retrieve the top 10 trending bills sorted by vote count in descending order.

    Returns:
        JSON response containing a list of serialized trending bills.
    """
    try:
        bills = Bill.query.order_by(Bill.vote_count.desc()).limit(10).all()
        return jsonify([serialize_bill(bill) for bill in bills])
    except Exception as e:
        app.logger.error(f"Error fetching trending bills: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/bills/<int:bill_id>/full", methods=["GET"])
def get_full_bill(bill_id):
    """
    API endpoint to retrieve full details for a specific bill by its id.

    Args:
        bill_id (int): The unique id of the bill.

    Returns:
        JSON response containing the serialized bill details or a 404 error if not found.
    """
    try:
        bill = db.session.get(Bill, bill_id)
        if not bill:
            return jsonify({"error": "Bill not found"}), 404

        if bill.url:
            bill.url = bill.url.replace("api.congress.gov", "www.congress.gov")

        return jsonify(serialize_bill(bill))
    except Exception as e:
        app.logger.error(f"Error fetching full bill: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/search", methods=["GET"])
def search_bills():
    """
    API endpoint to search bills based on a keyword.

    Query Parameters:
        keyword (str): The search keyword to look for in the bill's title, AI summary, or text preview.

    Returns:
        JSON response containing a list of serialized bills matching the search criteria.
    """
    try:
        keyword = request.args.get("keyword", "")
        if not keyword:
            return jsonify([])

        bills = Bill.query.filter(
            or_(
                Bill.title.ilike(f"%{keyword}%"),
                Bill.ai_summary.ilike(f"%{keyword}%"),
                Bill.text_preview.ilike(f"%{keyword}%")
            )
        ).limit(20).all()

        return jsonify([serialize_bill(bill) for bill in bills])
    except Exception as e:
        app.logger.error(f"Error in search: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/search_tfidf", methods=["GET"])
def search_bills_tfidf():
    """
    API endpoint to search bills using TF–IDF to rank documents based on relevance.
    
    Query Parameters:
        keyword (str): The search keyword to look for in the bill's title, AI summary, and text preview.
        
    Returns:
        JSON response containing a list of serialized bills matching the search criteria.
    """
    try:
        keyword = request.args.get("keyword", "").strip()
        if not keyword:
            return jsonify([])

        # Retrieve the prebuilt search entries.
        entries = BillSearchEntry.query.all()
        if not entries:
            return jsonify([])

        documents = [entry.combined_text for entry in entries]
        bill_ids = [entry.bill_id for entry in entries]

        # Initialize the vectorizer and compute the TF–IDF matrix.
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Transform the query into the TF–IDF vector space.
        query_vec = vectorizer.transform([keyword])
        
        # Compute cosine similarities.
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
        
        # Sort indices by similarity (highest first) and filter to include only positive matches.
        sorted_indices = similarities.argsort()[::-1]
        top_indices = [i for i in sorted_indices if similarities[i] > 0][:20]

        # Build a list of serialized bills in order of relevance.
        bills = []
        for idx in top_indices:
            bill = db.session.get(Bill, bill_ids[idx])
            if bill:
                bills.append(serialize_bill(bill))
        
        return jsonify(bills)
    
    except Exception as e:
        app.logger.error("Error in TF–IDF search: %s", e, exc_info=True)
        return jsonify({"error": "An error occurred during search."}), 500

@app.route("/api/bills/<int:bill_id>/vote", methods=["POST"])
@jwt_required()
def vote_on_bill(bill_id):
    """
    Endpoint to allow a user to vote on a bill.

    It handles three vote statuses:

    - "upvote" or "downvote": Casting or changing a vote.
    - "none": Removing an existing vote.

    It updates the Vote entity's demographic counters and the User's `voted_bills` accordingly.
    """
    try:
        data = request.get_json()
        vote_status = data.get("vote_status")
        
        if vote_status not in ["upvote", "downvote", "none"]:
            return jsonify({"error": "Invalid vote status. Must be 'upvote', 'downvote', or 'none'."}), 400

        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        bill = db.session.get(Bill, bill_id)
        if not bill:
            return jsonify({"error": "Bill not found."}), 404

        if user.age is None:
            return jsonify({"error": "User age not specified."}), 400

        if user.age < 18:
            age_category = "under_18"
        elif 18 <= user.age < 30:
            age_category = "18_to_30"
        elif 30 <= user.age < 60:
            age_category = "30_to_60"
        else:
            age_category = "60_plus"

        # Normalize demographics.
        gender = user.gender.lower() if user.gender else "other"
        if gender not in ["male", "female", "non-binary", "transgender", "other"]:
            gender = "other"

        ethnicity = user.ethnicity.lower() if user.ethnicity else "other"
        valid_ethnicities = [
            "hispanic or latino", "white", "black or african american", "asian",
            "native hawaiian or other pacific islander", "american indian or alaska native", "other"
        ]
        if ethnicity not in valid_ethnicities:
            ethnicity = "other"

        state = user.state.lower() if user.state else "other"
        valid_states = [
            "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga",
            "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md",
            "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj",
            "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc",
            "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy", "other"
        ]
        if state not in valid_states:
            state = "other"

        political_affiliation = user.political_affiliation.lower() if user.political_affiliation else "other"
        valid_political = [
            "democrat", "republican", "independent", "libertarian", "green",
            "conservative", "progressive", "moderate", "socialist", "communist", "other"
        ]
        if political_affiliation not in valid_political:
            political_affiliation = "other"

        # Get or create the vote record for the bill.
        vote_record = Vote.query.filter_by(bill_id=bill_id).first()
        if not vote_record:
            if vote_status != "none":
                vote_record = Vote(bill_id=bill_id, demographics=default_demographics())
                db.session.add(vote_record)
            else:
                return jsonify({"error": "No existing vote to remove for this bill."}), 400

        previous_vote = user.voted_bills.get(str(bill_id))

        # CASE 1: User has not voted yet.
        if previous_vote is None:
            if vote_status == "none":
                return jsonify({"error": "You haven't voted on this bill yet."}), 400

            # Increment demographics for the new vote.
            demo = vote_record.demographics[vote_status]
            demo["age_distribution"][age_category] = demo["age_distribution"].get(age_category, 0) + 1
            demo["gender_distribution"][gender] = demo["gender_distribution"].get(gender, 0) + 1
            demo["ethnicity_distribution"][ethnicity] = demo["ethnicity_distribution"].get(ethnicity, 0) + 1
            demo["state_distribution"][state] = demo["state_distribution"].get(state, 0) + 1
            demo["political_affiliation_distribution"][political_affiliation] = demo["political_affiliation_distribution"].get(political_affiliation, 0) + 1
            vote_record.demographics[vote_status] = demo

        
            if vote_status == "upvote":
                bill.upvote_count += 1
                bill.vote_count +=1
            if vote_status == "downvote":
                bill.downvote_count += 1
                bill.vote_count += 1
            user.voted_bills[str(bill_id)] = vote_status

        # CASE 2: User has already voted on this bill.
        else:
            if vote_status == "none":
                # Remove the vote: decrement demographics.
                old_demo = vote_record.demographics[previous_vote]
                old_demo["age_distribution"][age_category] = max(old_demo["age_distribution"].get(age_category, 0) - 1, 0)
                old_demo["gender_distribution"][gender] = max(old_demo["gender_distribution"].get(gender, 0) - 1, 0)
                old_demo["ethnicity_distribution"][ethnicity] = max(old_demo["ethnicity_distribution"].get(ethnicity, 0) - 1, 0)
                old_demo["state_distribution"][state] = max(old_demo["state_distribution"].get(state, 0) - 1, 0)
                old_demo["political_affiliation_distribution"][political_affiliation] = max(old_demo["political_affiliation_distribution"].get(political_affiliation, 0) - 1, 0)
                vote_record.demographics[previous_vote] = old_demo

                bill.vote_count = max(bill.vote_count - 1, 0)
                if previous_vote == "upvote":
                    bill.upvote_count = max(bill.upvote_count - 1, 0)
                elif previous_vote == "downvote":
                    bill.downvote_count = max(bill.downvote_count - 1, 0)
                if str(bill_id) in user.voted_bills:
                    del user.voted_bills[str(bill_id)]

            else:
                # If the vote is the same as before, nothing needs to change.
                if previous_vote == vote_status:
                    return jsonify({"message": "Vote already recorded with the same status."}), 200

                # Changing the vote: first remove the old vote's demographics.
                old_demo = vote_record.demographics[previous_vote]
                old_demo["age_distribution"][age_category] = max(old_demo["age_distribution"].get(age_category, 0) - 1, 0)
                old_demo["gender_distribution"][gender] = max(old_demo["gender_distribution"].get(gender, 0) - 1, 0)
                old_demo["ethnicity_distribution"][ethnicity] = max(old_demo["ethnicity_distribution"].get(ethnicity, 0) - 1, 0)
                old_demo["state_distribution"][state] = max(old_demo["state_distribution"].get(state, 0) - 1, 0)
                old_demo["political_affiliation_distribution"][political_affiliation] = max(old_demo["political_affiliation_distribution"].get(political_affiliation, 0) - 1, 0)
                vote_record.demographics[previous_vote] = old_demo

                # Then add the new vote's demographics.
                new_demo = vote_record.demographics[vote_status]
                new_demo["age_distribution"][age_category] = new_demo["age_distribution"].get(age_category, 0) + 1
                new_demo["gender_distribution"][gender] = new_demo["gender_distribution"].get(gender, 0) + 1
                new_demo["ethnicity_distribution"][ethnicity] = new_demo["ethnicity_distribution"].get(ethnicity, 0) + 1
                new_demo["state_distribution"][state] = new_demo["state_distribution"].get(state, 0) + 1
                new_demo["political_affiliation_distribution"][political_affiliation] = new_demo["political_affiliation_distribution"].get(political_affiliation, 0) + 1
                vote_record.demographics[vote_status] = new_demo

                if previous_vote == "upvote":
                    bill.upvote_count = max(bill.upvote_count - 1, 0)
                    bill.downvote_count += 1
                elif previous_vote == "downvote":
                    bill.downvote_count = max(bill.downvote_count - 1, 0)
                    bill.upvote_count += 1

                # Update the user's vote to the new status.
                user.voted_bills[str(bill_id)] = vote_status

        db.session.commit()
        return jsonify({
            "message": "Vote processed successfully",
            "vote": {
                "bill_id": bill_id,
                "vote_status": vote_status,
                "demographics": vote_record.demographics
            },
            "bill": {
                "id": bill.id,
                "vote_count": bill.vote_count,
                "upvote_count": bill.upvote_count,
                "downvote_count": bill.downvote_count
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/api/bills/<int:bill_id>/demographics", methods=["GET"])
def get_bill_demographics(bill_id):
    """
    Endpoint to retrieve demographic information for votes on a given bill.
    Returns the demographics data from the Vote record associated with the bill,
    or the default demographics if no votes have been recorded yet.
    """
    try:
        bill = db.session.get(Bill, bill_id)
        if not bill:
            return jsonify({"error": "Bill not found."}), 404

        vote_record = Vote.query.filter_by(bill_id=bill_id).first()
        if vote_record is None:
            demographics = default_demographics()
        else:
            demographics = vote_record.demographics

        return jsonify({
            "bill_id": bill_id,
            "demographics": demographics
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
