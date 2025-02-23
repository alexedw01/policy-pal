import pytest
import json
from datetime import datetime, timezone
from backend.app import app, db, Bill, serialize_bill

@pytest.fixture(scope="module")
def client():
    """
    Fixture for configuring the Flask application for testing.

    The application is set to testing mode and uses an in-memory SQLite database.
    The database tables are created before yielding the test client and cleaned up afterward.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_bills.db"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="module", autouse=True)
def populate_db(client):
    """
    Populate the database with test bill data.

    Adds two Bill records so that the endpoints have data available for testing.
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
                upvote_count=5,
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
                upvote_count=10,
                created_at=datetime(2023, 1, 2, tzinfo=timezone.utc)
            )
            db.session.add_all([bill1, bill2])
            db.session.commit()

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
            "text_preview", "full_text", "ai_summary", "upvote_count", "created_at", "updated_at"
        ]
        for key in expected_keys:
            assert key in serialized

def test_get_minimal_bills(client):
    """
    Test that the /api/bills-minimal endpoint returns a list of minimal bill data.
    """
    response = client.get("/api/bills-minimal")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2
    for bill in data:
        for key in ["id", "bill_number", "title", "latest_action_date", "ai_summary"]:
            assert key in bill

def test_get_bills_pagination(client):
    """
    Test the /api/bills endpoint with pagination and filtering by chamber.

    Verifies that pagination metadata is present and that filtering by chamber returns
    only bills from the specified chamber.
    """
    response = client.get("/api/bills")
    assert response.status_code == 200
    data = response.get_json()
    assert "bills" in data and "pagination" in data
    pagination = data["pagination"]
    for key in ["page", "per_page", "total", "pages"]:
        assert key in pagination

    response_house = client.get("/api/bills", query_string={"chamber": "House"})
    assert response_house.status_code == 200
    data_house = response_house.get_json()
    for bill in data_house["bills"]:
        if bill.get("origin_chamber"):
            assert bill["origin_chamber"].lower() == "house"

def test_get_trending_bills(client):
    """
    Test that the /api/bills/trending endpoint returns bills sorted by upvote_count
    in descending order and limits the results to 10.
    """
    response = client.get("/api/bills/trending")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) <= 10
    if len(data) > 1:
        first_upvotes = data[0]["upvote_count"]
        for bill in data[1:]:
            assert first_upvotes >= bill["upvote_count"]

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
    assert len(data) >= 1
    found = any("Test Bill One" in bill["title"] for bill in data)
    assert found
