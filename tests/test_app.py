from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
BASE_ACTIVITIES = deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(deepcopy(BASE_ACTIVITIES))


def test_get_activities_returns_data():
    # Arrange
    reset_activities()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant_for_mergington_email():
    # Arrange
    reset_activities()
    url = "/activities/Chess%20Club/signup?email=student@mergington.edu"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up student@mergington.edu for Chess Club"
    assert "student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_invalid_email_domain():
    # Arrange
    reset_activities()
    url = "/activities/Chess%20Club/signup?email=student@example.com"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Only @mergington.edu email addresses may register"
    assert "student@example.com" not in activities["Chess Club"]["participants"]


def test_duplicate_signup_is_rejected():
    # Arrange
    reset_activities()
    url = "/activities/Chess%20Club/signup?email=michael@mergington.edu"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    # Arrange
    reset_activities()
    url = "/activities/Chess%20Club/participants?email=michael@mergington.edu"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
