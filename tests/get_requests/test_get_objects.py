# GET coverage for collection retrieval, individual objects, and ID filtering.

import requests
from pytest import mark

# Shared endpoint definitions keep URLs consistent across the test suite.
from api_urls import OBJECTS_URLS

# Markers select the API operation and outcome; parametrization runs each input separately.


# Verifies that the collection returns a nonempty list with the expected object fields.
@mark.test
@mark.sanity
@mark.positive
def test_get_objects_returns_success():
    response = requests.get(OBJECTS_URLS.BASE, timeout=10)

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
@mark.sanity
@mark.positive
def test_get_object_by_id_returns_requested_object():
    response = requests.get(OBJECTS_URLS.object_by_id("1"), timeout=10)

    assert response.status_code == 200
    response_body = response.json()
    assert isinstance(response_body, dict)
    assert response_body["id"] == "1"
    assert isinstance(response_body["name"], str)
    assert response_body["name"]
    assert "data" in response_body


# Verifies that collection filtering returns exactly the requested IDs.
@mark.test
@mark.sanity
@mark.positive
def test_get_objects_filters_by_requested_ids():
    response = requests.get(
        OBJECTS_URLS.BASE, params={"id": ["1", "2"]}, timeout=10
    )

    assert response.status_code == 200
    response_body = response.json()
    assert isinstance(response_body, list)
    assert len(response_body) == 2
    assert {item["id"] for item in response_body} == {"1", "2"}


# Checks that nonexistent and negative IDs return a not-found error.
@mark.test
@mark.sanity
@mark.negative
@mark.parametrize(
    "object_id",
    ["pytest-missing-object-98a7f6d4", "-1"],
    ids=["nonexistent-id", "negative-id"],
)
def test_get_object_returns_not_found_for_unknown_id(object_id):
    response = requests.get(OBJECTS_URLS.object_by_id(object_id), timeout=10)

    assert response.status_code == 404
    assert response.json()["error"] == f"Object with id={object_id} was not found."


# Checks that a valid filter with no matches returns an empty collection.
@mark.test
@mark.positive
def test_get_objects_returns_empty_list_for_unknown_id_filter():
    response = requests.get(
        OBJECTS_URLS.BASE,
        params={"id": "pytest-missing-object-98a7f6d4"},
        timeout=10,
    )

    # Collection filtering succeeds even when no objects match the requested ID.
    assert response.status_code == 200
    assert response.json() == []
