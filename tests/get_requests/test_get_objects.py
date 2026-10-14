import requests
from pytest import mark

from api_urls import OBJECTS_URLS


@mark.test
@mark.positive
def test_get_objects_returns_success():
    response = requests.get(OBJECTS_URLS.BASE, timeout=10)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
