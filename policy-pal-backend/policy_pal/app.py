import os
import json
import time
from datetime import datetime, timedelta
import requests
import click
import openai
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
from bson.errors import InvalidId

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS", "PUT"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Authorization"]
    }
})

if not os.getenv("DATABASE_URL"):
    raise ValueError("No DATABASE_URL in environment")

app.config["MONGO_URI"] = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

try:
    mongo = PyMongo(app)
    mongo.db.bills.create_index([("congress", 1), ("bill_type", 1), ("bill_number", 1)], unique=True)
    mongo.db.bills.create_index([("title", "text")])
    mongo.db.upvotes.create_index([("user_id", 1), ("bill_id", 1)], unique=True)  
    mongo.db.upvotes.create_index([("created_at", -1)])
    print("MongoDB connected successfully")
except PyMongoError as e:
    print(f"MongoDB connection error: {e}")

mongo.db.users.create_index([("email", 1)], unique=True)
mongo.db.users.create_index([("username", 1)], unique=True)

CONGRESS_API_KEY = os.getenv("CONGRESS_API_KEY")
CONGRESS_API_BASE = "https://api.congress.gov/v3"
API_RATE_LIMIT = 2  

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

class CongressionalScraper:
    def __init__(self, mongo):
        self.mongo = mongo
        self.headers = {"X-API-Key": CONGRESS_API_KEY}
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < 1/API_RATE_LIMIT:
            time.sleep(1/API_RATE_LIMIT - time_since_last_request)
        self.last_request_time = time.time()

    def get_bill_details(self, url):
        """Fetch detailed bill information"""
        self._rate_limit()
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("bill", {})
            print(f"Error fetching bill details: Status {response.status_code}")
        except Exception as e:
            print(f"Exception fetching bill details: {e}")
        return None

    def get_bill_text(self, congress, bill_type, bill_number, full_text=False):
        """Fetch the bill text from congress.gov API."""
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
                    
     
                    htm_format = next((f for f in formats if f["type"] == "Formatted Text"), None)
                    if htm_format:
                        htm_url = htm_format["url"]
                        print(f"Fetching HTML from: {htm_url}")
                        self._rate_limit()
                        htm_response = requests.get(htm_url)
                        if (htm_response.status_code == 200):
                            soup = BeautifulSoup(htm_response.text, 'html.parser')
                            content = soup.find('pre')
                            if content:
                                text = content.get_text(separator=' ', strip=True)
                                if full_text:
                                    return text
                                return text[:1000] + "..." if len(text) > 1000 else text
                            else:
                                print("No pre tag found in HTM content")
                        else:
                            print(f"Failed to fetch HTM content: {htm_response.status_code}")
                    else:
                        print("No HTM format found")
                return None
                
            else:
                print(f"Error fetching bill texts: Status {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Exception fetching bill text: {str(e)}")
            print(f"Full error details: {repr(e)}")
            return None

    def process_bill(self, bill_data):
        """Process a single bill and store it in MongoDB."""
        try:
            congress = bill_data["congress"]
            bill_type = bill_data["type"]
            bill_number = bill_data["number"]
            
            print(f"Processing bill {bill_type}{bill_number}")

            detailed_bill = self.get_bill_details(bill_data["url"])
            if not detailed_bill:
                detailed_bill = bill_data  

            existing_bill = self.mongo.db.bills.find_one({
                "congress": congress,
                "bill_type": bill_type,
                "bill_number": bill_number
            })

            action_date = (detailed_bill.get("latestAction", {}).get("actionDate") or 
                         bill_data.get("latestAction", {}).get("actionDate") or 
                         bill_data.get("updateDate"))

            bill_text = self.get_bill_text(congress, bill_type, bill_number)
            full_text = self.get_bill_text(congress, bill_type, bill_number, full_text=True)
            ai_summary = None
            if bill_text:
                try:
                    ai_summary_response = openai.ChatCompletion.create(
                        model="gpt-4o",  
                        messages=[
                            {"role": "system", "content": "You are a professional congressional analyst. Summarize the following bill text concisely and objectively in 6-8 sentences."},
                            {"role": "user", "content": bill_text}
                        ],
                        max_tokens=300
                    )
                    ai_summary = ai_summary_response.choices[0].message.content
                    print(f"Generated AI summary: {ai_summary}")
                except Exception as e:
                    print(f"Error generating AI summary: {e}")
            congress_url = f"https://www.congress.gov/bill/{congress}th-congress/{bill_type.lower()}/{bill_number}"
            new_bill = {
                "congress": congress,
                "bill_type": bill_type,
                "bill_number": bill_number,
                "title": detailed_bill.get("title", bill_data.get("title", "")),
                "latest_action_date": datetime.strptime(action_date, "%Y-%m-%d") if action_date else datetime.utcnow(),
                "origin_chamber": bill_data.get("originChamber", ""),
                "sponsor": detailed_bill.get("sponsor", {}).get("name", "Unknown"),
                "latest_action": detailed_bill.get("latestAction", bill_data.get("latestAction", {})),
                "update_date": datetime.strptime(bill_data["updateDate"], "%Y-%m-%d"),
                "url": congress_url,
                "text_preview": bill_text,
                "full_text": full_text,  
                "ai_summary": ai_summary,
                "upvote_count": 0,
                "created_at": datetime.utcnow()
            }

            if existing_bill:
                update_fields = {
                    "title": new_bill["title"],
                    "latest_action": new_bill["latest_action"],
                    "update_date": new_bill["update_date"],
                    "text_preview": new_bill["text_preview"],
                    "ai_summary": new_bill["ai_summary"],
                    "updated_at": datetime.utcnow()
                }
                self.mongo.db.bills.update_one(
                    {"_id": existing_bill["_id"]},
                    {"$set": update_fields}
                )
                print(f"Updated existing bill {bill_type}{bill_number}")
                return False
            
            self.mongo.db.bills.insert_one(new_bill)
            print(f"Successfully inserted bill {bill_type}{bill_number}")
            return True
                
        except Exception as e:
            print(f"Error processing bill: {e}")
            print("Bill data:", json.dumps(bill_data, indent=2))
            return False

    def batch_scrape(self, congress, offset=0, limit=20):
        """Perform batch scraping of bills."""
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
                return processed_count, len(bills), data.get("pagination", {}).get("count", 0)
            else:
                print(f"Error in batch scrape: Status {response.status_code}")
                return 0, 0, 0
        except Exception as e:
            print(f"Exception in batch scrape: {e}")
            return 0, 0, 0

    def daily_update(self):
        """Perform daily update of new and modified bills."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        current_congress = 118  
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
                print(f"Error in daily update: Status {response.status_code}")
                return 0
        except Exception as e:
            print(f"Exception in daily update: {e}")
            return 0

def scheduled_update():
    """Function to be called by scheduler"""
    with app.app_context():
        scraper = CongressionalScraper(mongo)
        processed = scraper.daily_update()
        print(f"Scheduled update completed: processed {processed} bills")

def scheduled_batch_scrape():
    """Function to scrape 3 new bills every minute"""
    with app.app_context():
        scraper = CongressionalScraper(mongo)
        tracking = mongo.db.scrape_tracking.find_one({"type": "offset"})
        current_offset = tracking["offset"] if tracking else 0
        
        processed, total, available = scraper.batch_scrape(congress=118, offset=current_offset, limit=3)
        
        new_offset = current_offset + 3
        mongo.db.scrape_tracking.update_one(
            {"type": "offset"},
            {"$set": {"offset": new_offset}},
            upsert=True
        )
        
        print(f"Scheduled batch completed: processed {processed} bills. Next offset: {new_offset}")


scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_batch_scrape, trigger="interval", minutes=1)
scheduler.add_job(func=scheduled_update, trigger="interval", hours=24)
scheduler.start()
def track_bill_view(user_id, bill_id, action_type="view"):
    try:
        activity = {
            "user_id": user_id,
            "bill_id": bill_id,
            "action_type": action_type,
            "created_at": datetime.utcnow()
        }
        mongo.db.user_activity.insert_one(activity)
        

        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"activity_metrics.bills_viewed": 1}}
        )
    except Exception as e:
        print(f"Error tracking activity: {str(e)}")
@app.cli.command("scrape-bills")
@click.option("--congress", default=118, help="Congress number to scrape")
@click.option("--offset", default=0, help="Starting offset")
@click.option("--limit", default=20, help="Number of bills to fetch")
def scrape_bills(congress, offset, limit):
    """Scrape bills from the congress.gov API."""
    scraper = CongressionalScraper(mongo)
    processed, total, available = scraper.batch_scrape(congress, offset, limit)
    click.echo(f"Processed {processed} new bills out of {total} fetched bills.")
    click.echo(f"Total bills available: {available}")

@app.cli.command("scrape-status")
def scrape_status():
    """Show current scraping status."""
    try:
        tracking = mongo.db.scrape_tracking.find_one({"type": "offset"})
        total_bills = mongo.db.bills.count_documents({})
        
        click.echo(f"Current offset: {tracking['offset'] if tracking else 0}")
        click.echo(f"Total bills in database: {total_bills}")
        

        click.echo("\nMost recent bills:")
        recent_bills = mongo.db.bills.find().sort("created_at", -1).limit(5)
        for bill in recent_bills:
            click.echo(f"{bill['bill_type']}{bill['bill_number']} - {bill['title'][:100]}...")
            
    except Exception as e:
        click.echo(f"Error checking status: {e}")

@app.cli.command("list-bills")
def list_bills():
    """List stored bills in the database."""
    try:
        bills = mongo.db.bills.find().limit(5)
        for bill in bills:
            click.echo("\n" + "="*80)
            click.echo(f"Basic Info:")
            click.echo(f"Title: {bill['title']}")
            click.echo(f"Congress: {bill['congress']}")
            click.echo(f"Bill ID: {bill['bill_type']}{bill['bill_number']}")
            click.echo(f"Origin Chamber: {bill.get('origin_chamber', 'Unknown')}")
            
            click.echo("\nDates:")
            click.echo(f"Latest Action Date: {bill.get('latest_action_date')}")
            click.echo(f"Update Date: {bill['update_date']}")
            click.echo(f"Created At: {bill['created_at']}")
            
            click.echo("\nActions and Status:")
            click.echo(f"Latest Action: {json.dumps(bill['latest_action'], indent=2)}")
            
            click.echo("\nMetadata:")
            click.echo(f"URL: {bill.get('url', 'No URL')}")
            click.echo(f"Sponsor: {bill.get('sponsor', 'No sponsor info')}")
            click.echo(f"Upvote Count: {bill.get('upvote_count', 0)}")
            
            if bill.get('text_preview'):
                click.echo("\nText Preview:")
                click.echo(bill['text_preview'])
            
            if bill.get('ai_summary'):
                click.echo("\nAI Summary:")
                click.echo(bill['ai_summary'])
                
            click.echo("="*80)
    except Exception as e:
        click.echo(f"Error listing bills: {e}")

def serialize_bill(bill):
    """Helper function to serialize bill for JSON response"""
    bill_copy = bill.copy()
    bill_copy['_id'] = str(bill_copy['_id'])
    
    for date_field in ['created_at', 'update_date', 'latest_action_date']:
        if date_field in bill_copy and bill_copy[date_field]:
            bill_copy[date_field] = bill_copy[date_field].isoformat()
    
    return bill_copy

@app.route("/api/bills", methods=["GET"])
def get_bills():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort', 'created_at')
        sort_dir = int(request.args.get('sort_dir', -1))
        chamber = request.args.get('chamber')  
        query = {}
        if chamber and chamber != 'all':
            query['origin_chamber'] = chamber
        
        total = mongo.db.bills.count_documents(query)
        bills = list(mongo.db.bills.find(query)
                    .sort(sort_by, sort_dir)
                    .skip((page - 1) * per_page)
                    .limit(per_page))
        
        return jsonify({
            'bills': [serialize_bill(bill) for bill in bills],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        print(f"Error fetching bills: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/bills/trending", methods=["GET"])
def get_trending_bills():
    try:
        bills = list(mongo.db.bills.find().sort("upvote_count", -1).limit(10))
        return jsonify([serialize_bill(bill) for bill in bills])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bills/<bill_id>/full", methods=["GET"])
def get_full_bill(bill_id):
    try:
        bill = mongo.db.bills.find_one({"_id": ObjectId(bill_id)})
        if not bill:
            return jsonify({"error": "Bill not found"}), 404


        if bill.get('url'):
            bill['url'] = bill['url'].replace(
                'api.congress.gov', 
                'www.congress.gov'
            )
        

        bill["_id"] = str(bill["_id"])
        return jsonify(bill)
    except Exception as e:
        print(f"Error fetching full bill: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/search", methods=["GET"])
def search_bills():
    try:
        keyword = request.args.get("keyword", "")
        if not keyword:
            return jsonify([])
        

        query = {
            "$or": [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"ai_summary": {"$regex": keyword, "$options": "i"}},
                {"text_preview": {"$regex": keyword, "$options": "i"}}
            ]
        }
        
        bills = list(mongo.db.bills.find(query).limit(20))
        return jsonify([serialize_bill(bill) for bill in bills])
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bills/<bill_id>/upvote", methods=["POST"])
@jwt_required()
def upvote_bill(bill_id):
    try:
        user_id = get_jwt_identity()
        
        try:
            bill_obj_id = ObjectId(bill_id)
        except InvalidId:
            return jsonify({"error": "Invalid bill ID"}), 400


        existing_vote = mongo.db.upvotes.find_one({
            "user_id": user_id,
            "bill_id": bill_id
        })
        
        if existing_vote:
            return jsonify({"error": "Already voted"}), 400


        upvote = {
            "user_id": user_id,
            "bill_id": bill_id,
            "created_at": datetime.utcnow()
        }
        mongo.db.upvotes.insert_one(upvote)


        mongo.db.bills.update_one(
            {"_id": bill_obj_id},
            {"$inc": {"upvote_count": 1}}
        )

        return jsonify({"message": "Upvote successful"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

        if not email or not password or not username:
            return jsonify({"error": "Missing required fields"}), 400


        if mongo.db.users.find_one({"email": email}):
            return jsonify({"error": "Email already registered"}), 409
        hashed_password = generate_password_hash(password)
        user = {
            "email": email,
            "password": hashed_password,
            "username": username,
            "created_at": datetime.utcnow()
        }
        
        mongo.db.users.insert_one(user)
        access_token = create_access_token(identity=str(user["_id"]))
        
        return jsonify({
            "access_token": access_token,
            "user": {
                "email": email,
                "username": username
            }
        }), 201

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.json
        user = mongo.db.users.find_one({"email": data['email']})
        
        if user and check_password_hash(user['password'], data['password']):
            access_token = create_access_token(identity=str(user['_id']))
            return jsonify({
                "access_token": access_token,
                "user": {
                    "id": str(user['_id']),
                    "username": user['username'],
                    "email": user['email']
                }
            }), 200
        
        return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bills/<bill_id>/analytics", methods=["GET"])
def get_bill_analytics(bill_id):
    try:
        pipeline = [
            {"$match": {"bill_id": bill_id}},
            {"$group": {
                "_id": "$user_demographics.age_range", 
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        demographics = list(mongo.db.upvotes.aggregate(pipeline))
        
        return jsonify({
            "total_upvotes": mongo.db.upvotes.count_documents({"bill_id": bill_id}),
            "demographic_breakdown": demographics
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/api/test", methods=["GET"])
def test_connection():
    return jsonify({"status": "ok", "message": "API is working"})

@app.route("/api/analytics/trending", methods=["GET"])
def get_trending_analytics():
    try:
        yesterday = datetime.utcnow() - timedelta(days=1)
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": yesterday}
                }
            },
            {
                "$group": {
                    "_id": "$bill_id",
                    "views": {"$sum": 1},
                    "upvotes": {"$sum": {"$cond": [{"$eq": ["$action_type", "upvote"]}, 1, 0]}},
                }
            },
            {"$sort": {"views": -1}},
            {"$limit": 10}
        ]
        
        trending = list(mongo.db.user_activity.aggregate(pipeline))
        
        for trend in trending:
            bill = mongo.db.bills.find_one({"_id": ObjectId(trend["_id"])})
            if bill:
                trend["bill"] = serialize_bill(bill)
                
        return jsonify(trending)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analytics/user/<user_id>", methods=["GET"])
@jwt_required()
def get_user_analytics(user_id):
    try:
        if user_id != get_jwt_identity():
            return jsonify({"error": "Unauthorized"}), 403
        activity = mongo.db.user_activity.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$action_type",
                "count": {"$sum": 1},
                "last_action": {"$max": "$created_at"}
            }}
        ])

        upvoted_bills = mongo.db.upvotes.find({"user_id": user_id})
        bill_ids = [vote["bill_id"] for vote in upvoted_bills]
        bills = mongo.db.bills.find({"_id": {"$in": bill_ids}})
        
        return jsonify({
            "activity_summary": list(activity),
            "upvoted_bills": [serialize_bill(bill) for bill in bills]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/profile", methods=["GET", "PUT"])
@jwt_required()
def manage_profile():
    user_id = get_jwt_identity()
    
    if request.method == "GET":
        try:
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return jsonify({"error": "User not found"}), 404
                
            return jsonify({
                "profile": user.get("profile", {}),
                "activity_metrics": user.get("activity_metrics", {})
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == "PUT":
        try:
            data = request.get_json()
            valid_fields = ["age_range", "state", "political_interests", 
                          "notification_preferences"]
            update_data = {
                f"profile.{k}": v for k, v in data.items() 
                if k in valid_fields
            }
            
            result = mongo.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": update_data,
                    "$currentDate": {"updated_at": True}
                }
            )
            
            if result.modified_count:
                return jsonify({"message": "Profile updated successfully"})
            return jsonify({"error": "No changes made"}), 400
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)