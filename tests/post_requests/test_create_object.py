import requests
from pytest import mark

from api_urls import OBJECTS_URLS


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


@mark.test
@mark.negative
def test_post_object_creation_fails_when_payload_schema_is_incorrect():
    payload = ["not", "a", "valid", "object", "payload"]

    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)
    response_body = response.json()

    assert response.status_code == 400
    assert response_body["error"] == "Invalid request body"
