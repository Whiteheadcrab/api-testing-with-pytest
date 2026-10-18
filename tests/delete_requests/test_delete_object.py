# DELETE coverage for removing objects and handling missing resources.

from uuid import uuid4

import requests
from pytest import fixture, mark

# Shared endpoint definitions keep URLs consistent across the test suite.
from api_urls import OBJECTS_URLS

# Markers select the API operation and outcome; parametrization runs each input separately.


# Creates a separate object for each test and cleans it up even if an assertion fails.
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
        # Give the test the created resource; execution resumes here during teardown.
        yield response_body
    finally:
        # Remove the resource after the test, including when the test fails.
        response = requests.delete(object_url, timeout=10)
        # Successful DELETE tests have already removed the object.
        assert response.status_code in (200, 404)


# Verifies the deletion confirmation and checks that GET can no longer retrieve the object.
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


# Prepares each missing-resource scenario; indirect parametrization supplies request.param.
@fixture
def missing_object_id(request):
    if request.param == "already-deleted":
        # Only this scenario needs a real object and the existing cleanup fixture.
        created = request.getfixturevalue("created_object")
        object_id = created["id"]
        response = requests.delete(OBJECTS_URLS.object_by_id(object_id), timeout=10)
        assert response.status_code == 200
        return object_id
    if request.param == "negative-id":
        return "-1"
    # A random ID avoids accidentally targeting an existing resource.
    return f"pytest-missing-{uuid4().hex}"


# All missing-resource scenarios must reject DELETE and remain unavailable through GET.
@mark.test
@mark.delete
@mark.negative
@mark.parametrize(
    "missing_object_id",
    ["nonexistent-id", "negative-id", "already-deleted"],
    indirect=True,
    ids=["nonexistent-id", "negative-id", "already-deleted"],
)
def test_delete_object_fails_when_object_does_not_exist(missing_object_id):
    object_url = OBJECTS_URLS.object_by_id(missing_object_id)
    response = requests.delete(object_url, timeout=10)

    assert response.status_code == 404
    assert missing_object_id in response.json()["error"]

    response = requests.get(object_url, timeout=10)
    assert response.status_code == 404
    assert missing_object_id in response.json()["error"]
