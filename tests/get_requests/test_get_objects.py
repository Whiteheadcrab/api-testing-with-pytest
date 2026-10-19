# GET coverage for collection retrieval, individual objects, and ID filtering.

import requests
from pytest import mark

# Shared endpoint definitions keep URLs consistent across the test suite.
from api_urls import OBJECTS_URLS
from config import REQUEST_TIMEOUT

# Every test in this module calls a running API and requires explicit opt-in.
pytestmark = mark.live

# Markers select the API operation and outcome; parametrization runs each input separately.


# Verifies that the collection returns a nonempty list with the expected object fields.
@mark.test
@mark.get
@mark.sanity
@mark.positive
def test_get_objects_returns_success():
    response = requests.get(OBJECTS_URLS.BASE, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    response_body = response.json()
    assert isinstance(response_body, list)
    assert response_body, "The public sample collection should contain objects."
    for item in response_body:
        assert isinstance(item, dict)
        assert {"id", "name", "data"} <= item.keys()
        assert isinstance(item["id"], str)
        assert item["id"]
        assert isinstance(item["name"], str)
        assert item["name"]


# Verifies that requesting a known ID returns the matching object.
@mark.test
@mark.get
@mark.sanity
@mark.positive
@mark.parametrize("object_id", ["1", "2"], ids=["first-object", "second-object"])
def test_get_object_by_id_returns_requested_object(object_id):
    response = requests.get(OBJECTS_URLS.object_by_id(object_id), timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    response_body = response.json()
    assert isinstance(response_body, dict)
    assert response_body["id"] == object_id
    assert isinstance(response_body["name"], str)
    assert response_body["name"]
    assert "data" in response_body


# Verifies that collection filtering returns exactly the requested IDs.
@mark.test
@mark.get
@mark.sanity
@mark.positive
@mark.parametrize(
    "object_ids",
    [["1"], ["1", "2"]],
    ids=["single-id", "multiple-ids"],
)
def test_get_objects_filters_by_requested_ids(object_ids):
    response = requests.get(
        OBJECTS_URLS.BASE, params={"id": object_ids}, timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 200
    response_body = response.json()
    assert isinstance(response_body, list)
    assert len(response_body) == len(object_ids)
    assert {item["id"] for item in response_body} == set(object_ids)


# Checks that nonexistent and negative IDs return a not-found error.
@mark.test
@mark.get
@mark.sanity
@mark.negative
@mark.parametrize(
    "object_id",
    ["pytest-missing-object-98a7f6d4", "-1"],
    ids=["nonexistent-id", "negative-id"],
)
def test_get_object_returns_not_found_for_unknown_id(object_id):
    response = requests.get(OBJECTS_URLS.object_by_id(object_id), timeout=REQUEST_TIMEOUT)

    assert response.status_code == 404
    assert response.json()["error"] == f"Object with id={object_id} was not found."


# Checks that a valid filter with no matches returns an empty collection.
@mark.test
@mark.get
@mark.positive
def test_get_objects_returns_empty_list_for_unknown_id_filter():
    response = requests.get(
        OBJECTS_URLS.BASE,
        params={"id": "pytest-missing-object-98a7f6d4"},
        timeout=REQUEST_TIMEOUT,
    )

    # Collection filtering succeeds even when no objects match the requested ID.
    assert response.status_code == 200
    assert response.json() == []
