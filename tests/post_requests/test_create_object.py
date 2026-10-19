# POST coverage for successful creation and invalid request payloads.

import requests
from pytest import mark, param

# Shared endpoint definitions keep URLs consistent across the test suite.
from api_urls import OBJECTS_URLS
from config import REQUEST_TIMEOUT

# Markers select the API operation and outcome; parametrization runs each input separately.


# Verifies that creation returns the submitted fields and a generated ID.
@mark.test
@mark.positive
def test_post_object_creates_new_object():
    payload = {
        "name": "QA Automation Test Object",
        "data": {
            "created_by": "pytest",
            "request_type": "post",
        },
    }

    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=REQUEST_TIMEOUT)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == payload["data"]
    assert response_body["id"]


# Each parameter retains its own expected-failure reason for unsupported validation.
@mark.test
@mark.negative
@mark.parametrize(
    "payload",
    [
        param(
            {"data": {"created_by": "pytest", "request_type": "post"}},
            marks=mark.xfail(reason="API currently accepts object creation without a name."),
            id="missing-name",
        ),
        param(
            {"name": "QA Automation Invalid Data Object", "data": "not-an-object"},
            marks=mark.xfail(reason="API currently accepts non-object data values."),
            id="invalid-data-format",
        ),
    ],
)
def test_post_object_creation_rejects_invalid_fields(payload):
    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 400


# Checks that an array payload is rejected because the endpoint expects a JSON object.
@mark.test
@mark.negative
def test_post_object_creation_fails_when_payload_schema_is_incorrect():
    payload = ["not", "a", "valid", "object", "payload"]

    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=REQUEST_TIMEOUT)
    response_body = response.json()

    assert response.status_code == 400
    assert response_body["error"] == "Invalid request body"
