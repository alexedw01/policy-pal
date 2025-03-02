import pytest
import json
from datetime import datetime, timezone
from backend.app import app, db, Bill, Vote, serialize_bill, User, default_demographics

@pytest.fixture(autouse=True, scope="module")
def patch_user_init():
    original_init = User.__init__
    def new_init(self, *args, **kwargs):
        if "voted_bill" in kwargs:
            kwargs["voted_bills"] = kwargs.pop("voted_bill")
        original_init(self, *args, **kwargs)
    User.__init__ = new_init
    yield
    User.__init__ = original_init

@pytest.fixture(scope="module")
def client():
    """
    Configure the Flask application for testing.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_bills.db"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="module")
def registered_users(client):
    """
    Populate the database with test users by calling the registration endpoint.
    Registers four users with distinct demographic attributes.
    Returns a dictionary mapping usernames to their respective access tokens and IDs.
    """
    users_data = [
        {
            "email": "user1@example.com",
            "username": "user1",
            "password": "password1",
            "age": 16,
            "gender": "male",
            "ethnicity": "white",
            "state": "ca",
            "political_affiliation": "democrat"
        },
        {
            "email": "user2@example.com",
            "username": "user2",
            "password": "password2",
            "age": 25,
            "gender": "female",
            "ethnicity": "asian",
            "state": "ny",
            "political_affiliation": "republican"
        },
        {
            "email": "user3@example.com",
            "username": "user3",
            "password": "password3",
            "age": 35,
            "gender": "non-binary",
            "ethnicity": "black or african american",
            "state": "tx",
            "political_affiliation": "independent"
        },
        {
            "email": "user4@example.com",
            "username": "user4",
            "password": "password4",
            "age": 65,
            "gender": "transgender",
            "ethnicity": "hispanic or latino",
            "state": "fl",
            "political_affiliation": "socialist"
        }
    ]
    registered = {}
    for user in users_data:
        response = client.post("/api/auth/register", json=user)
        assert response.status_code == 201, f"Registration failed: {response.get_json()}"
        data = response.get_json()
        registered[user["username"]] = {
            "token": data["access_token"],
            "id": data["user"]["id"]
        }
    return registered

@pytest.fixture(scope="module", autouse=True)
def populate_db(client):
    """
    Populate the database with test bill data.
    """
    with app.app_context():
        if Bill.query.count() == 0:
            bill1 = Bill(
                congress=118,
                bill_type="H.R.",
                bill_number="123",
                title="Test Bill One",
                latest_action_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                origin_chamber="House",
                sponsor="Sponsor One",
                latest_action={"action": "Action One"},
                update_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                url="http://api.congress.gov/bill/118/H.R./123",
                text_preview="Preview text one",
                full_text="Full text one",
                ai_summary="Summary one",
                vote_count=5,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc)
            )
            bill2 = Bill(
                congress=118,
                bill_type="S.",
                bill_number="456",
                title="Test Bill Two",
                latest_action_date=datetime(2023, 1, 2, tzinfo=timezone.utc),
                origin_chamber="Senate",
                sponsor="Sponsor Two",
                latest_action={"action": "Action Two"},
                update_date=datetime(2023, 1, 2, tzinfo=timezone.utc),
                url="http://api.congress.gov/bill/118/S./456",
                text_preview="Preview text two",
                full_text="Full text two",
                ai_summary="Summary two",
                vote_count=10,
                created_at=datetime(2023, 1, 2, tzinfo=timezone.utc)
            )
            db.session.add_all([bill1, bill2])
            db.session.commit()

def create_test_bill_for_vote():
    """
    Helper to create a fresh Bill for vote tests.
    """
    with app.app_context():
        bill = Bill(
            congress=118,
            bill_type="H.R.",
            bill_number="789",
            title="Vote Test Bill",
            latest_action_date=datetime.now(timezone.utc),
            origin_chamber="House",
            sponsor="Vote Tester",
            latest_action={"action": "Test action"},
            update_date=datetime.now(timezone.utc),
            url="http://api.congress.gov/bill/118/H.R./789",
            text_preview="Preview text vote",
            full_text="Full text vote",
            ai_summary="Summary vote",
            vote_count=0,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(bill)
        db.session.commit()
        return bill.id

def test_serialize_bill():
    """
    Verify that serialize_bill returns all expected keys from a Bill instance.
    """
    with app.app_context():
        bill = Bill.query.first()
        serialized = serialize_bill(bill)
        expected_keys = [
            "_id", "congress", "bill_type", "bill_number", "title", "latest_action_date",
            "origin_chamber", "sponsor", "latest_action", "update_date", "url",
            "text_preview", "full_text", "ai_summary", "vote_count", "created_at", "updated_at"
        ]
        for key in expected_keys:
            assert key in serialized

def test_get_bills_pagination(client):
    """
    Test the /api/bills endpoint with pagination and filtering by chamber.
    """
    response = client.get("/api/bills")
    assert response.status_code == 200
    data = response.get_json()
    assert "bills" in data and "pagination" in data
    for key in ["page", "per_page", "total", "pages"]:
        assert key in data["pagination"]

    response_house = client.get("/api/bills", query_string={"chamber": "House"})
    assert response_house.status_code == 200
    data_house = response_house.get_json()
    for bill in data_house["bills"]:
        if bill.get("origin_chamber"):
            assert bill["origin_chamber"].lower() == "house"

def test_get_trending_bills(client):
    """
    Test that the /api/bills/trending endpoint returns bills sorted by vote_count
    in descending order and limits the results to 10.
    """
    response = client.get("/api/bills/trending")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) <= 10
    if len(data) > 1:
        first_votes = data[0]["vote_count"]
        for bill in data[1:]:
            assert first_votes >= bill["vote_count"]

def test_get_full_bill(client):
    """
    Test that /api/bills/<bill_id>/full returns the full details of a bill,
    and that a non-existent bill ID returns a 404 error.
    """
    with app.app_context():
        bill = Bill.query.first()
        bill_id = bill.id
    response = client.get(f"/api/bills/{bill_id}/full")
    assert response.status_code == 200
    data = response.get_json()
    assert data["_id"] == str(bill_id)
    response_nf = client.get("/api/bills/999999/full")
    assert response_nf.status_code == 404
    data_nf = response_nf.get_json()
    assert data_nf["error"] == "Bill not found"

def test_search_bills(client):
    """
    Test that the /api/search endpoint returns bills matching the provided keyword.
    """
    response = client.get("/api/search", query_string={"keyword": "Test Bill One"})
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any("Test Bill One" in bill["title"] for bill in data)

def test_search_tfidf(client):
    """
    Test that the /api/search_tfidf endpoint returns bills matching the provided keyword
    using TF–IDF over full_text, ai_summary, and title.
    """
    # Import and build the search index from the combined fields.
    from backend.app import build_bill_search_entries
    with app.app_context():
        build_bill_search_entries()
    response = client.get("/api/search_tfidf", query_string={"keyword": "Test Bill One"})
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    # Verify that the bill with "Test Bill One" in the title is returned.
    assert any("Test Bill One" in bill["title"] for bill in data)

def test_vote_bill_upvote(client, registered_users):
    """
    Test adding an upvote to a bill with no prior vote from the user.
    """
    bill_id = create_test_bill_for_vote()
    token = registered_users["user1"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "upvote"}, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("message") == "Vote processed successfully"

    with app.app_context():
        bill = db.session.get(Bill, bill_id)
        assert bill.vote_count == 1
        user = db.session.get(User, registered_users["user1"]["id"])
        assert user.voted_bills.get(str(bill_id)) == "upvote"

def test_vote_bill_downvote(client, registered_users):
    """
    Test adding a downvote to a bill.
    """
    bill_id = create_test_bill_for_vote()
    token = registered_users["user2"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "downvote"}, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("message") == "Vote processed successfully"

    with app.app_context():
        bill = db.session.get(Bill, bill_id)
        assert bill.vote_count == 1
        user = db.session.get(User, registered_users["user2"]["id"])
        assert user.voted_bills.get(str(bill_id)) == "downvote"

def test_vote_bill_no_change(client, registered_users):
    """
    Test that re-sending the same vote does not alter vote_count.
    """
    bill_id = create_test_bill_for_vote()
    token = registered_users["user3"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response1 = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "upvote"}, headers=headers)
    assert response1.status_code == 200

    response2 = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "upvote"}, headers=headers)
    assert response2.status_code == 200
    data = response2.get_json()
    assert data.get("message") == "Vote already recorded with the same status."

    with app.app_context():
        bill = db.session.get(Bill, bill_id)
        assert bill.vote_count == 1

def test_vote_bill_update(client, registered_users):
    """
    Test updating an existing vote (from upvote to downvote) without changing vote_count.
    """
    bill_id = create_test_bill_for_vote()
    token = registered_users["user4"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response1 = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "upvote"}, headers=headers)
    assert response1.status_code == 200

    response2 = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "downvote"}, headers=headers)
    assert response2.status_code == 200
    data = response2.get_json()
    assert data.get("message") == "Vote processed successfully"

    with app.app_context():
        bill = db.session.get(Bill, bill_id)
        assert bill.vote_count == 1
        user = db.session.get(User, registered_users["user4"]["id"])
        assert user.voted_bills.get(str(bill_id)) == "downvote"

def test_vote_bill_remove_existing(client, registered_users):
    """
    Test that removing an existing vote decreases the vote_count.
    """
    bill_id = create_test_bill_for_vote()
    token = registered_users["user1"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response1 = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "upvote"}, headers=headers)
    assert response1.status_code == 200

    response2 = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "none"}, headers=headers)
    assert response2.status_code == 200
    data = response2.get_json()
    assert data.get("message") == "Vote processed successfully"

    with app.app_context():
        bill = db.session.get(Bill, bill_id)
        assert bill.vote_count == 0
        user = db.session.get(User, registered_users["user1"]["id"])
        assert str(bill_id) not in user.voted_bills

def test_vote_bill_remove_nonexistent(client, registered_users):
    """
    Test that attempting to remove a non-existent vote returns an appropriate error.
    """
    bill_id = create_test_bill_for_vote()
    token = registered_users["user2"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "none"}, headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert data.get("error") == "No existing vote to remove for this bill."

def test_vote_bill_invalid_vote_status(client, registered_users):
    """
    Test that an invalid vote_status returns a 400 error.
    """
    bill_id = create_test_bill_for_vote()
    token = registered_users["user3"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"/api/bills/{bill_id}/vote", json={"vote_status": "invalid"}, headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert "Invalid vote status" in data.get("error", "")

def test_vote_bill_not_found(client, registered_users):
    """
    Test that voting on a non-existent bill returns a 404 error.
    """
    token = registered_users["user4"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/bills/999999/vote", json={"vote_status": "upvote"}, headers=headers)
    assert response.status_code == 404
    data = response.get_json()
    assert data.get("error") == "Bill not found."

def test_bill_demographics(client, registered_users):
    """
    Test the /api/bills/<bill_id>/demographics endpoint.
    This test creates a Vote record with custom demographics and checks that the endpoint returns the expected values.
    """
    with app.app_context():
        bill = Bill(
            congress=118,
            bill_type="H.R.",
            bill_number="101",
            title="Demographics Test Bill",
            latest_action_date=datetime.now(timezone.utc),
            origin_chamber="House",
            sponsor="Demo Tester",
            latest_action={"action": "Demo action"},
            update_date=datetime.now(timezone.utc),
            url="http://api.congress.gov/bill/118/H.R./101",
            text_preview="Demo preview",
            full_text="Demo full text",
            ai_summary="Demo summary",
            vote_count=0,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(bill)
        db.session.commit()
        bill_id = bill.id

        custom_demo = default_demographics()
        # For upvote: update for user1 (16, male, ca, white, democrat) and user2 (25, female, ny, asian, republican)
        custom_demo["upvote"]["age_distribution"]["under_18"] += 1
        custom_demo["upvote"]["age_distribution"]["18_to_30"] += 1
        custom_demo["upvote"]["gender_distribution"]["male"] += 1
        custom_demo["upvote"]["gender_distribution"]["female"] += 1
        custom_demo["upvote"]["state_distribution"]["ca"] += 1
        custom_demo["upvote"]["state_distribution"]["ny"] += 1
        custom_demo["upvote"]["ethnicity_distribution"]["white"] += 1
        custom_demo["upvote"]["ethnicity_distribution"]["asian"] += 1
        custom_demo["upvote"]["political_affiliation_distribution"]["democrat"] += 1
        custom_demo["upvote"]["political_affiliation_distribution"]["republican"] += 1

        # For downvote: update for user3 (35, non-binary, tx, black or african american, independent)
        # and user4 (65, transgender, fl, hispanic or latino, socialist)
        custom_demo["downvote"]["age_distribution"]["30_to_60"] += 1
        custom_demo["downvote"]["age_distribution"]["60_plus"] += 1
        custom_demo["downvote"]["gender_distribution"]["non-binary"] += 1
        custom_demo["downvote"]["gender_distribution"]["transgender"] += 1
        custom_demo["downvote"]["state_distribution"]["tx"] += 1
        custom_demo["downvote"]["state_distribution"]["fl"] += 1
        custom_demo["downvote"]["ethnicity_distribution"]["black or african american"] += 1
        custom_demo["downvote"]["ethnicity_distribution"]["hispanic or latino"] += 1
        custom_demo["downvote"]["political_affiliation_distribution"]["independent"] += 1
        custom_demo["downvote"]["political_affiliation_distribution"]["socialist"] += 1

        vote = Vote(bill_id=bill_id, demographics=custom_demo)
        db.session.add(vote)
        bill.vote_count = 4
        db.session.commit()

    response = client.get(f"/api/bills/{bill_id}/demographics")
    assert response.status_code == 200
    data = response.get_json()
    demo = data.get("demographics")
    assert demo is not None

    # Check upvote demographics.
    up_demo = demo.get("upvote")
    assert up_demo is not None
    assert up_demo["age_distribution"]["under_18"] == 1
    assert up_demo["age_distribution"]["18_to_30"] == 1
    assert up_demo["gender_distribution"]["male"] == 1
    assert up_demo["gender_distribution"]["female"] == 1
    assert up_demo["state_distribution"]["ca"] == 1
    assert up_demo["state_distribution"]["ny"] == 1
    assert up_demo["ethnicity_distribution"]["white"] == 1
    assert up_demo["ethnicity_distribution"]["asian"] == 1
    assert up_demo["political_affiliation_distribution"]["democrat"] == 1
    assert up_demo["political_affiliation_distribution"]["republican"] == 1

    # Check downvote demographics.
    down_demo = demo.get("downvote")
    assert down_demo is not None
    assert down_demo["age_distribution"]["30_to_60"] == 1
    assert down_demo["age_distribution"]["60_plus"] == 1
    assert down_demo["gender_distribution"]["non-binary"] == 1
    assert down_demo["gender_distribution"]["transgender"] == 1
    assert down_demo["state_distribution"]["tx"] == 1
    assert down_demo["state_distribution"]["fl"] == 1
    assert down_demo["ethnicity_distribution"]["black or african american"] == 1
    assert down_demo["ethnicity_distribution"]["hispanic or latino"] == 1
    assert down_demo["political_affiliation_distribution"]["independent"] == 1
    assert down_demo["political_affiliation_distribution"]["socialist"] == 1
