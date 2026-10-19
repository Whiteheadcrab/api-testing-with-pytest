# Basic smoke checks for the supported object API operations.

import requests
from pytest import mark

# Shared endpoint definitions keep URLs consistent across the test suite.
from api_urls import OBJECTS_URLS
from config import REQUEST_TIMEOUT

# Every test in this module calls a running API and requires explicit opt-in.
pytestmark = mark.live


# Verifies that the objects collection is available and returns a JSON list.
@mark.test
@mark.get
@mark.smoke
@mark.positive
def test_get_objects_returns_success():
    response = requests.get(OBJECTS_URLS.BASE, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Verifies that a new object can be created with a valid request payload.
@mark.test
@mark.post
@mark.smoke
@mark.positive
def test_post_object_creates_new_object(post_object):
    payload = {
        "name": "QA Automation Test Object",
        "data": {
            "created_by": "pytest",
            "test_type": "smoke",
        },
    }

    response = post_object(payload)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == payload["data"]
    assert response_body["id"]


# Verifies that an existing object can be fully replaced with PUT.
@mark.test
@mark.put
@mark.smoke
@mark.positive
def test_put_object_updates_existing_object(created_object):
    object_id = created_object["id"]
    payload = {
        "name": "QA Automation Updated Object",
        "data": {
            "created_by": "pytest",
            "test_type": "smoke",
            "update_type": "full",
        },
    }

    response = requests.put(OBJECTS_URLS.object_by_id(object_id), json=payload, timeout=REQUEST_TIMEOUT)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == payload["data"]


# Verifies that an existing object can be partially updated with PATCH.
@mark.test
@mark.patch
@mark.smoke
@mark.positive
def test_patch_object_updates_existing_object_partially(created_object):
    object_id = created_object["id"]
    payload = {
        "name": "QA Automation Patched Object",
    }

    response = requests.patch(OBJECTS_URLS.object_by_id(object_id), json=payload, timeout=REQUEST_TIMEOUT)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["name"] == payload["name"]


# Verifies that an existing object can be deleted successfully.
@mark.test
@mark.delete
@mark.smoke
@mark.positive
def test_delete_object_removes_existing_object(created_object):
    object_id = created_object["id"]

    response = requests.delete(OBJECTS_URLS.object_by_id(object_id), timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert object_id in response.json()["message"]
