# PATCH coverage for partial updates, persistence, and rejected requests.

from uuid import uuid4

import requests
from pytest import fixture, mark

# Shared endpoint definitions keep URLs consistent across the test suite.
from api_urls import OBJECTS_URLS
from config import REQUEST_TIMEOUT

# Every test in this module calls a running API and requires explicit opt-in.
pytestmark = mark.live

# Markers select the API operation and outcome; parametrization runs each input separately.


# Creates a separate object for each test and cleans it up even if an assertion fails.
@fixture
def created_object():
    payload = {
        "name": "QA Automation Test Object",
        "data": {"created_by": "pytest", "request_type": "patch"},
    }
    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    response_body = response.json()
    object_url = OBJECTS_URLS.object_by_id(response_body["id"])

    try:
        # Give the test the created resource; execution resumes here during teardown.
        yield response_body
    finally:
        # Remove the resource after the test, including when the test fails.
        response = requests.delete(object_url, timeout=REQUEST_TIMEOUT)
        assert response.status_code == 200


# Verifies each update persists while fields omitted from the payload remain unchanged.
@mark.test
@mark.patch
@mark.positive
@mark.parametrize(
    "payload",
    [
        {"name": "QA Automation Patched Object"},
        {"data": {"created_by": "pytest", "updated": True}},
        {
            "name": "QA Automation Updated Object",
            "data": {"created_by": "pytest", "price": 123.45},
        },
    ],
    ids=["name-only", "data-only", "name-and-data"],
)
def test_patch_object_updates_requested_fields(created_object, payload):
    # Overlay the requested fields on the original values to check untouched fields too.
    expected = {**created_object, **payload}
    object_url = OBJECTS_URLS.object_by_id(created_object["id"])
    response = requests.patch(object_url, json=payload, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["id"] == created_object["id"]
    assert response_body["name"] == expected["name"]
    assert response_body["data"] == expected["data"]
    assert response_body["updatedAt"]

    # Verify persisted values as well as the immediate PATCH response.
    response = requests.get(object_url, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200
    assert response.json()["name"] == expected["name"]
    assert response.json()["data"] == expected["data"]


# Checks that PATCH rejects an ID that does not belong to an existing object.
@mark.test
@mark.patch
@mark.negative
def test_patch_object_fails_when_object_does_not_exist():
    # A random ID avoids accidentally targeting an existing resource.
    object_id = f"pytest-missing-{uuid4().hex}"
    payload = {"name": "QA Automation Patched Object"}

    response = requests.patch(
        OBJECTS_URLS.object_by_id(object_id), json=payload, timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 404
    assert object_id in response.json()["error"]


# Checks both invalid JSON and an array payload, then confirms the object is unchanged.
@mark.test
@mark.patch
@mark.negative
@mark.parametrize(
    "request_body",
    ['["not", "an", "object"]', '{"name":'],
    ids=["array-instead-of-object", "malformed-json"],
)
def test_patch_object_rejects_invalid_request_body(created_object, request_body):
    object_url = OBJECTS_URLS.object_by_id(created_object["id"])
    response = requests.patch(
        object_url,
        # Send raw text so malformed JSON reaches the server without client serialization.
        data=request_body,
        headers={"Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Invalid request body"

    response = requests.get(object_url, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200
    response_body = response.json()
    assert response_body["name"] == created_object["name"]
    assert response_body["data"] == created_object["data"]
