from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module

client = TestClient(app_module.app)
original_activities = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_activities))
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_activities))


def test_get_activities_returns_all_available_activities():
    # Arrange
    expected_activity_names = set(original_activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert set(activities.keys()) == expected_activity_names
    assert activities["Chess Club"]["description"] == original_activities["Chess Club"]["description"]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Basketball Team"
    new_email = "alex@mergington.edu"
    assert new_email not in app_module.activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Gym Class"
    email_to_remove = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email_to_remove},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email_to_remove} from {activity_name}"
    assert email_to_remove not in app_module.activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Soccer Club"
    missing_email = "ghost@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"


def test_unregister_unknown_activity_returns_404():
    # Arrange
    unknown_activity_name = "Unknown Activity"
    email = "test@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{unknown_activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
