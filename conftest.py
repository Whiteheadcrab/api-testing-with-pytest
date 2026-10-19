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
