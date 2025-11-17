import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

# Keep an original snapshot of activities so tests can reset state between runs
original_activities = copy.deepcopy(app_module.activities)
client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

# Keep an original snapshot of activities so tests can reset state between runs
original_activities = copy.deepcopy(app_module.activities)
client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(original_activities)
    yield


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect a known activity from the seeded data
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]


def test_signup_and_duplicate():
    activity = "Chess Club"
    email = "testuser@mergington.edu"

    # Sign up should succeed
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Duplicate signup should return 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_signup_activity_not_found():
    resp = client.post("/activities/NotAnActivity/signup?email=a@b.com")
    assert resp.status_code == 404


def test_unregister_and_errors():
    activity = "Chess Club"
    email = "tempremove@mergington.edu"

    # Add the email first
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    # Now remove it
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")

    # Removing again should 404
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404

    # Removing from non-existent activity
    resp = client.delete("/activities/Nope/participants?email=x@y.com")
    assert resp.status_code == 404
