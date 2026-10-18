# POST coverage for successful creation and invalid request payloads.

import requests
from pytest import mark

# Shared endpoint definitions keep URLs consistent across the test suite.
from api_urls import OBJECTS_URLS

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

    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == payload["data"]
    assert response_body["id"]


# Documents expected name validation; xfail records that the API currently accepts it.
@mark.test
@mark.negative
@mark.xfail(reason="API currently accepts object creation without a name.")
def test_post_object_creation_fails_when_name_is_missing():
    payload = {
        "data": {
            "created_by": "pytest",
            "request_type": "post",
        },
    }

    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)

    assert response.status_code == 400


# Documents expected data validation; xfail records that the API accepts non-object data.
@mark.test
@mark.negative
@mark.xfail(reason="API currently accepts non-object data values.")
def test_post_object_creation_fails_when_data_format_is_incorrect():
    payload = {
        "name": "QA Automation Invalid Data Object",
        "data": "not-an-object",
    }

    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)

    assert response.status_code == 400


# Checks that an array payload is rejected because the endpoint expects a JSON object.
@mark.test
@mark.negative
def test_post_object_creation_fails_when_payload_schema_is_incorrect():
    payload = ["not", "a", "valid", "object", "payload"]

    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)
    response_body = response.json()

    assert response.status_code == 400
    assert response_body["error"] == "Invalid request body"
