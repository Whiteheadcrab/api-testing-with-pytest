from uuid import uuid4

import requests
from pytest import fixture, mark

from api_urls import OBJECTS_URLS


@fixture
def created_object():
    payload = {
        "name": "QA Automation Test Object",
        "data": {"created_by": "pytest", "request_type": "delete"},
    }
    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)

    assert response.status_code == 200
    response_body = response.json()
    object_url = OBJECTS_URLS.object_by_id(response_body["id"])

    try:
        yield response_body
    finally:
        response = requests.delete(object_url, timeout=10)
        # Successful DELETE tests have already removed the object.
        assert response.status_code in (200, 404)


@mark.test
@mark.delete
@mark.positive
def test_delete_object_removes_existing_object(created_object):
    object_id = created_object["id"]
    object_url = OBJECTS_URLS.object_by_id(object_id)
    response = requests.delete(object_url, timeout=10)

    assert response.status_code == 200
    assert response.json()["message"] == (
        f"Object with id = {object_id} has been deleted."
    )

    response = requests.get(object_url, timeout=10)
    assert response.status_code == 404
    assert object_id in response.json()["error"]


@mark.test
@mark.delete
@mark.negative
def test_delete_object_fails_when_object_is_already_deleted(created_object):
    object_id = created_object["id"]
    object_url = OBJECTS_URLS.object_by_id(object_id)
    response = requests.delete(object_url, timeout=10)
    assert response.status_code == 200

    response = requests.delete(object_url, timeout=10)

    assert response.status_code == 404
    assert object_id in response.json()["error"]

    response = requests.get(object_url, timeout=10)
    assert response.status_code == 404
    assert object_id in response.json()["error"]


@mark.test
@mark.delete
@mark.negative
@mark.parametrize(
    "object_id",
    [f"pytest-missing-{uuid4().hex}", "-1"],
    ids=["nonexistent-id", "negative-id"],
)
def test_delete_object_fails_when_object_does_not_exist(object_id):
    response = requests.delete(OBJECTS_URLS.object_by_id(object_id), timeout=10)

    assert response.status_code == 404
    assert object_id in response.json()["error"]
