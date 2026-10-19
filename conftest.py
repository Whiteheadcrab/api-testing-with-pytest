"""Keep frequent local checks separate from explicitly requested live API runs."""

import pytest
import requests


# Opting in is separate from marker selection: -m live alone still skips API calls.
def pytest_addoption(parser):
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Allow live API tests to run against API_BASE_URL.",
    )


# Skip before fixture setup so skipped tests cannot create or delete API objects.
def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-live"):
        return
    skip_live = pytest.mark.skip(reason="Live API test; enable with --run-live.")
    for item in items:
        if item.get_closest_marker("live"):
            item.add_marker(skip_live)


# Catch accidental requests calls in tests intended to run without the API.
@pytest.fixture(autouse=True)
def prevent_offline_http(request, monkeypatch):
    if request.node.get_closest_marker("live"):
        return

    def reject_request(*args, **kwargs):
        pytest.fail("HTTP requests require a live-marked test and --run-live.")

    monkeypatch.setattr(requests.sessions.Session, "request", reject_request)


# Track successful creations before returning so failed assertions and xfail tests
# still clean up. Each finalizer runs independently, even if another cleanup fails.
@pytest.fixture
def post_object(request):
    from api_urls import OBJECTS_URLS
    from config import REQUEST_TIMEOUT

    def post(payload):
        response = requests.post(OBJECTS_URLS.BASE, json=payload, timeout=REQUEST_TIMEOUT)
        if 200 <= response.status_code < 300:
            body = response.json()
            if isinstance(body, dict) and body.get("id"):
                object_url = OBJECTS_URLS.object_by_id(body["id"])

                def cleanup():
                    result = requests.delete(object_url, timeout=REQUEST_TIMEOUT)
                    # DELETE tests may already have removed the resource.
                    assert result.status_code in (200, 404), (
                        f"Cleanup failed for {object_url}: HTTP {result.status_code}"
                    )

                request.addfinalizer(cleanup)
        return response

    return post


# Give each update/delete test its own object through the same tracked POST path.
@pytest.fixture
def created_object(post_object, request):
    operation = next(
        (marker.name for marker in request.node.iter_markers()
         if marker.name in {"get", "post", "put", "patch", "delete"}),
        "setup",
    )
    payload = {
        "name": "QA Automation Test Object",
        "data": {"created_by": "pytest", "request_type": operation},
    }
    response = post_object(payload)
    assert response.status_code == 200
    return response.json()
