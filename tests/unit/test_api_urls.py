"""Check environment-to-endpoint integration in an isolated Python process."""

import json
import os
from pathlib import Path
import subprocess
import sys

from pytest import mark


pytestmark = [mark.test, mark.unit, mark.positive]
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Fresh imports must use the supplied environment, including string and integer IDs.
@mark.parametrize(
    "base_url, expected_base",
    [
        (None, "https://api.restful-api.dev"),
        ("http://localhost:8000/", "http://localhost:8000"),
        ("https://example.test/api/", "https://example.test/api"),
    ],
    ids=["default", "local-service", "base-path"],
)
def test_api_urls_use_environment(base_url, expected_base):
    # Set configuration only in the child process; never change the active test run.
    environment = os.environ.copy()
    environment.pop("API_BASE_URL", None)
    environment["API_TIMEOUT"] = "10"
    if base_url is not None:
        environment["API_BASE_URL"] = base_url

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json; from api_urls import OBJECTS_URLS; "
            "print(json.dumps([OBJECTS_URLS.BASE, "
            "OBJECTS_URLS.object_by_id(1), OBJECTS_URLS.object_by_id('custom-id')]))",
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout) == [
        f"{expected_base}/objects",
        f"{expected_base}/objects/1",
        f"{expected_base}/objects/custom-id",
    ]
