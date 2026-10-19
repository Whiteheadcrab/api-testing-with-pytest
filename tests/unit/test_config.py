"""Validate environment settings locally without importing cached configuration."""

from pathlib import Path
from runpy import run_path

from pytest import fixture, mark, raises


pytestmark = [mark.test, mark.unit]
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.py"


# Isolate each case from the developer's shell settings and from module caching.
@fixture
def load_config(monkeypatch):
    monkeypatch.delenv("API_BASE_URL", raising=False)
    monkeypatch.delenv("API_TIMEOUT", raising=False)

    def load(**overrides):
        for name, value in overrides.items():
            monkeypatch.setenv(name, value)
        return run_path(str(CONFIG_PATH))

    return load


# Default runs should retain the original public endpoint and ten-second timeout.
@mark.positive
def test_config_defaults(load_config):
    config = load_config()
    assert config["BASE_URL"] == "https://api.restful-api.dev"
    assert config["REQUEST_TIMEOUT"] == 10


# Verify custom hosts, base paths, whitespace trimming, and trailing-slash handling.
@mark.positive
@mark.parametrize(
    "base_url, expected",
    [
        ("http://localhost:8000", "http://localhost:8000"),
        ("https://example.test/api/", "https://example.test/api"),
        (" https://example.test/api/// ", "https://example.test/api"),
    ],
    ids=["local-service", "base-path", "trim-whitespace-and-slashes"],
)
def test_config_base_url_override(load_config, base_url, expected):
    assert load_config(API_BASE_URL=base_url)["BASE_URL"] == expected


# Requests supports both whole and fractional timeout values.
@mark.positive
@mark.parametrize("timeout", ["1", "2.5"], ids=["whole-seconds", "fractional-seconds"])
def test_config_timeout_override(load_config, timeout):
    assert load_config(API_TIMEOUT=timeout)["REQUEST_TIMEOUT"] == float(timeout)


# Invalid timeout settings must fail before any API request can be sent.
@mark.negative
@mark.parametrize(
    "timeout", ["", "abc", "0", "-1", "nan", "inf"],
    ids=["empty", "text", "zero", "negative", "nan", "infinity"],
)
def test_config_rejects_invalid_timeout(load_config, timeout):
    with raises(ValueError, match="API_TIMEOUT"):
        load_config(API_TIMEOUT=timeout)


# Reject addresses that cannot be used safely as an API base endpoint.
@mark.negative
@mark.parametrize(
    "base_url",
    ["", "relative/path", "ftp://localhost", "http://", "https://example.test?q=1", "https://example.test#part"],
    ids=["empty", "relative", "unsupported-scheme", "missing-host", "query", "fragment"],
)
def test_config_rejects_invalid_base_url(load_config, base_url):
    with raises(ValueError, match="API_BASE_URL"):
        load_config(API_BASE_URL=base_url)
