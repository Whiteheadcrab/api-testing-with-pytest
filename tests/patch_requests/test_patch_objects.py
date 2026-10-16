from uuid import uuid4

import requests
from pytest import fixture, mark

from api_urls import OBJECTS_URLS


@fixture
def created_object():
    payload = {
        "name": "QA Automation Test Object",
        "data": {"created_by": "pytest", "request_type": "patch"},
    }
    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)

    assert response.status_code == 200
    response_body = response.json()
    object_url = OBJECTS_URLS.object_by_id(response_body["id"])

    try:
        yield response_body
    finally:
        response = requests.delete(object_url, timeout=10)
        assert response.status_code == 200


@mark.test
@mark.patch
@mark.positive
def test_patch_object_updates_name(created_object):
    payload = {"name": "QA Automation Patched Object"}
    response = requests.patch(
        OBJECTS_URLS.object_by_id(created_object["id"]), json=payload, timeout=10
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["id"] == created_object["id"]
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == created_object["data"]


@mark.test
@mark.patch
@mark.positive
def test_patch_object_updates_data_without_changing_name(created_object):
    payload = {"data": {"created_by": "pytest", "updated": True}}
    object_url = OBJECTS_URLS.object_by_id(created_object["id"])
    response = requests.patch(object_url, json=payload, timeout=10)

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["id"] == created_object["id"]
    assert response_body["name"] == created_object["name"]
    assert response_body["data"] == payload["data"]

    response = requests.get(object_url, timeout=10)
    assert response.status_code == 200
    assert response.json()["data"] == payload["data"]
    assert response.json()["name"] == created_object["name"]


@mark.test
@mark.patch
@mark.positive
def test_patch_object_updates_name_and_data(created_object):
    payload = {
        "name": "QA Automation Updated Object",
        "data": {"created_by": "pytest", "price": 123.45},
    }
    object_url = OBJECTS_URLS.object_by_id(created_object["id"])
    response = requests.patch(object_url, json=payload, timeout=10)

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["id"] == created_object["id"]
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == payload["data"]
    assert response_body["updatedAt"]

    response = requests.get(object_url, timeout=10)
    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]
    assert response.json()["data"] == payload["data"]


@mark.test
@mark.patch
@mark.negative
def test_patch_object_fails_when_object_does_not_exist():
    object_id = f"pytest-missing-{uuid4().hex}"
    payload = {"name": "QA Automation Patched Object"}

    response = requests.patch(
        OBJECTS_URLS.object_by_id(object_id), json=payload, timeout=10
    )

    assert response.status_code == 404
    assert object_id in response.json()["error"]


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
        data=request_body,
        headers={"Content-Type": "application/json"},
        timeout=10,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Invalid request body"

    response = requests.get(object_url, timeout=10)
    assert response.status_code == 200
    response_body = response.json()
    assert response_body["name"] == created_object["name"]
    assert response_body["data"] == created_object["data"]
