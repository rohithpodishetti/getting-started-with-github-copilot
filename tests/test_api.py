"""
Test suite for the Mergington High School API

Tests follow the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a TestClient instance for making API requests."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities database to its initial state before each test.
    
    This fixture runs automatically before each test to ensure test isolation.
    """
    # Arrange: Store original activities
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and tournaments",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "marcus@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis lessons and friendly matches",
            "schedule": "Tuesdays and Thursdays, 3:00 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu", "lucas@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Learn and perform music with other students",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu", "benjamin@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore physics, chemistry, and biology through hands-on experiments",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ryan@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    # Act: Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup: Reset again after test completes
    activities.clear()
    activities.update(original_activities)


# =============================================================================
# GET / - Root endpoint tests
# =============================================================================

def test_root_redirects_to_static_index(client):
    """Test that the root endpoint redirects to the static index.html page."""
    # Arrange: Client is ready from fixture
    
    # Act: Request the root endpoint
    response = client.get("/", follow_redirects=False)
    
    # Assert: Should redirect to static index.html
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


# =============================================================================
# GET /activities - List all activities tests
# =============================================================================

def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities with correct structure."""
    # Arrange: Activities are set up by reset_activities fixture
    
    # Act: Request all activities
    response = client.get("/activities")
    
    # Assert: Should return 200 with all 9 activities
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_returns_correct_structure(client):
    """Test that each activity has the required fields."""
    # Arrange: Activities are set up by reset_activities fixture
    
    # Act: Request all activities
    response = client.get("/activities")
    
    # Assert: Each activity should have required fields
    data = response.json()
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


# =============================================================================
# POST /activities/{activity_name}/signup - Signup tests
# =============================================================================

def test_signup_for_activity_success(client):
    """Test successful signup adds participant to activity."""
    # Arrange: Prepare test data
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    initial_count = len(activities[activity]["participants"])
    
    # Act: Sign up for the activity
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert: Should succeed and add participant
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == initial_count + 1


def test_signup_for_nonexistent_activity(client):
    """Test signup for activity that doesn't exist returns 404."""
    # Arrange: Prepare test data with invalid activity
    email = "student@mergington.edu"
    activity = "Nonexistent Activity"
    
    # Act: Attempt to sign up for nonexistent activity
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert: Should return 404 error
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_participant(client):
    """Test that signing up twice for same activity returns 400 error."""
    # Arrange: Use an existing participant
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    # Act: Attempt to sign up again
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert: Should return 400 error for duplicate
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_with_url_encoded_activity_name(client):
    """Test signup with URL-encoded activity name (spaces)."""
    # Arrange: Prepare test data with activity containing spaces
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    encoded_activity = "Chess%20Club"
    
    # Act: Sign up using URL-encoded activity name
    response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
    
    # Assert: Should succeed with encoded name
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_case_sensitive_activity_name(client):
    """Test that activity names are case-sensitive."""
    # Arrange: Prepare test data with incorrect case
    email = "student@mergington.edu"
    activity = "chess club"  # lowercase instead of "Chess Club"
    
    # Act: Attempt signup with incorrect case
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert: Should return 404 (case-sensitive)
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# =============================================================================
# DELETE /activities/{activity_name}/unregister - Unregister tests
# =============================================================================

def test_unregister_from_activity_success(client):
    """Test successful unregistration removes participant from activity."""
    # Arrange: Use existing participant
    email = "michael@mergington.edu"
    activity = "Chess Club"
    initial_count = len(activities[activity]["participants"])
    assert email in activities[activity]["participants"]
    
    # Act: Unregister from the activity
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    
    # Assert: Should succeed and remove participant
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == initial_count - 1


def test_unregister_from_nonexistent_activity(client):
    """Test unregister from activity that doesn't exist returns 404."""
    # Arrange: Prepare test data with invalid activity
    email = "student@mergington.edu"
    activity = "Nonexistent Activity"
    
    # Act: Attempt to unregister from nonexistent activity
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    
    # Assert: Should return 404 error
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_not_registered(client):
    """Test unregistering participant who isn't registered returns 404."""
    # Arrange: Use email not in the activity
    email = "notregistered@mergington.edu"
    activity = "Chess Club"
    assert email not in activities[activity]["participants"]
    
    # Act: Attempt to unregister non-participant
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    
    # Assert: Should return 404 error
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"


def test_unregister_with_url_encoded_activity_name(client):
    """Test unregister with URL-encoded activity name (spaces)."""
    # Arrange: Use existing participant and encode activity name
    email = "michael@mergington.edu"
    activity = "Chess Club"
    encoded_activity = "Chess%20Club"
    
    # Act: Unregister using URL-encoded activity name
    response = client.delete(f"/activities/{encoded_activity}/unregister?email={email}")
    
    # Assert: Should succeed with encoded name
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


# =============================================================================
# Integration tests - Full workflow
# =============================================================================

def test_signup_and_unregister_workflow(client):
    """Test complete workflow: signup -> verify -> unregister -> verify."""
    # Arrange: Prepare test data
    email = "workflow@mergington.edu"
    activity = "Programming Class"
    
    # Act & Assert: Sign up
    signup_response = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_response.status_code == 200
    assert email in activities[activity]["participants"]
    
    # Act & Assert: Verify it appears in activities list
    get_response = client.get("/activities")
    assert email in get_response.json()[activity]["participants"]
    
    # Act & Assert: Unregister
    unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert unregister_response.status_code == 200
    assert email not in activities[activity]["participants"]
    
    # Act & Assert: Verify removed from activities list
    get_response2 = client.get("/activities")
    assert email not in get_response2.json()[activity]["participants"]


def test_multiple_signups_different_activities(client):
    """Test that a student can sign up for multiple different activities."""
    # Arrange: Prepare test data
    email = "multisport@mergington.edu"
    activity1 = "Chess Club"
    activity2 = "Programming Class"
    activity3 = "Gym Class"
    
    # Act: Sign up for multiple activities
    response1 = client.post(f"/activities/{activity1}/signup?email={email}")
    response2 = client.post(f"/activities/{activity2}/signup?email={email}")
    response3 = client.post(f"/activities/{activity3}/signup?email={email}")
    
    # Assert: Should succeed for all activities
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
    assert email in activities[activity1]["participants"]
    assert email in activities[activity2]["participants"]
    assert email in activities[activity3]["participants"]
