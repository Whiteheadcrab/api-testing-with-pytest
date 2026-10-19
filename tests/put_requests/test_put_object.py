# PUT coverage for replacement, persistence, and rejected requests.

from uuid import uuid4

import requests
from pytest import mark

# Shared endpoint definitions keep URLs consistent across the test suite.
from api_urls import OBJECTS_URLS
from config import REQUEST_TIMEOUT

# Every test in this module calls a running API and requires explicit opt-in.
pytestmark = mark.live

# Markers select the API operation and outcome; parametrization runs each input separately.


# Verifies replacement and persistence for populated data and for clearing existing data.
@mark.test
@mark.put
@mark.positive
@mark.parametrize(
    "payload",
    [
        {
            "name": "QA Automation Updated Object",
            "data": {"created_by": "pytest", "price": 123.45},
        },
        {"name": "QA Automation Replaced Object", "data": {}},
    ],
    ids=["replace-name-and-data", "clear-existing-data"],
)
def test_put_object_updates_name_and_data(created_object, payload):
    object_url = OBJECTS_URLS.object_by_id(created_object["id"])
    response = requests.put(object_url, json=payload, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["id"] == created_object["id"]
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == payload["data"]
    assert response_body["updatedAt"]

    # Retrieve the object independently to confirm the replacement was persisted.
    response = requests.get(object_url, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]
    assert response.json()["data"] == payload["data"]


# Checks that PUT returns a not-found error for a nonexistent object.
@mark.test
@mark.put
@mark.negative
def test_put_object_fails_when_object_does_not_exist():
    # A random ID avoids accidentally targeting an existing resource.
    object_id = f"pytest-missing-{uuid4().hex}"
    payload = {
        "name": "QA Automation Updated Object",
        "data": {"created_by": "pytest", "request_type": "put"},
    }

    response = requests.put(
        OBJECTS_URLS.object_by_id(object_id), json=payload, timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 404
    assert object_id in response.json()["error"]


# Checks both invalid JSON and an array payload, then confirms the object is unchanged.
@mark.test
@mark.put
@mark.negative
@mark.parametrize(
    "request_body",
    ['["not", "an", "object"]', '{"name":'],
    ids=["array-instead-of-object", "malformed-json"],
)
def test_put_object_rejects_invalid_request_body(created_object, request_body):
    object_url = OBJECTS_URLS.object_by_id(created_object["id"])
    response = requests.put(
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
