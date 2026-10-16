import requests
from pytest import mark

from api_urls import OBJECTS_URLS


@mark.test
@mark.patch
@mark.positive
def test_patch_object_updates_name():
    payload = {
        "name": "QA Automation Test Object",
        "data": {"created_by": "pytest", "request_type": "patch"},
    }
    response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=10)

    assert response.status_code == 200
    object_id = response.json()["id"]
    object_url = OBJECTS_URLS.object_by_id(object_id)

    try:
        patch_payload = {"name": "QA Automation Patched Object"}
        response = requests.patch(object_url, json=patch_payload, timeout=10)

        assert response.status_code == 200
        response_body = response.json()
        assert response_body["id"] == object_id
        assert response_body["name"] == patch_payload["name"]
        assert response_body["data"] == payload["data"]
    finally:
        response = requests.delete(object_url, timeout=10)
        assert response.status_code == 200
