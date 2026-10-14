import requests
from pytest import mark

from api_urls import OBJECTS_URLS


# Verifies that the objects collection is available and returns a JSON list.
@mark.test
@mark.smoke
@mark.positive
def test_get_objects_returns_success():
    response = requests.get(OBJECTS_URLS.BASE, timeout=10)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Verifies that a new object can be created with a valid request payload.
@mark.test
@mark.smoke
@mark.positive
def test_post_object_creates_new_object():
    payload = {
        "name": "QA Automation Test Object",
        "data": {
            "created_by": "pytest",
            "test_type": "smoke",
        },
    }

    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == payload["data"]
    assert response_body["id"]


# Verifies that an existing object can be fully replaced with PUT.
@mark.test
@mark.smoke
@mark.positive
def test_put_object_updates_existing_object():
    object_id = _create_test_object()
    payload = {
        "name": "QA Automation Updated Object",
        "data": {
            "created_by": "pytest",
            "test_type": "smoke",
            "update_type": "full",
        },
    }

    response = requests.put(OBJECTS_URLS.object_by_id(object_id), json=payload, timeout=10)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == payload["data"]


# Verifies that an existing object can be partially updated with PATCH.
@mark.test
@mark.smoke
@mark.positive
def test_patch_object_updates_existing_object_partially():
    object_id = _create_test_object()
    payload = {
        "name": "QA Automation Patched Object",
    }

    response = requests.patch(OBJECTS_URLS.object_by_id(object_id), json=payload, timeout=10)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["name"] == payload["name"]


# Verifies that an existing object can be deleted successfully.
@mark.test
@mark.smoke
@mark.positive
def test_delete_object_removes_existing_object():
    object_id = _create_test_object()

    response = requests.delete(OBJECTS_URLS.object_by_id(object_id), timeout=10)

    assert response.status_code == 200
    assert object_id in response.json()["message"]


# Creates a temporary object for tests that require an existing resource.
def _create_test_object() -> str:
    payload = {
        "name": "QA Automation Temporary Object",
        "data": {
            "created_by": "pytest",
            "test_type": "smoke",
        },
    }

    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)

    assert response.status_code == 200
    return response.json()["id"]
