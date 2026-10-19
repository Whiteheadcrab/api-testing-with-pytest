# API Testing With Pytest

Python API test automation project built with `pytest` and `requests`.

The project is intended to demonstrate a clean, maintainable approach to REST API testing, starting with basic CRUD coverage and growing into a reusable API testing framework.

## Current Scope

The initial version focuses on organizing API endpoint URLs for a public test service:

```text
https://api.restful-api.dev
```

The selected API supports standard REST operations:

- `GET`
- `POST`
- `PUT`
- `PATCH`
- `DELETE`

## Tech Stack

- Python
- pytest
- requests
- Git / GitHub

## Project Structure

```text
.
|-- api_urls.py
|-- config.py
|-- pytest.ini
|-- requirements.txt
|-- tests/
|   |-- smoke_tests/
|   |   `-- test_basic_api_requests.py
|   |-- get_requests/
|   |-- post_requests/
|   |-- put_requests/
|   |-- patch_requests/
|   `-- delete_requests/
|-- .gitignore
`-- README.md
```

## Design Direction

The framework will be developed incrementally with a focus on:

- clear separation between test data, endpoints, and test logic
- readable assertions with meaningful failure output
- reusable request helpers instead of duplicated request code
- stable fixtures for setup and cleanup
- practical test coverage for full API workflows

## Environment Configuration

`config.py` reads these environment variables when Python starts:

| Variable | Default | Purpose |
| --- | --- | --- |
| `API_BASE_URL` | `https://api.restful-api.dev` | API base address; `/objects` is appended by `api_urls.py` |
| `API_TIMEOUT` | `10` | Timeout in seconds for every request, including fixture setup and cleanup |

Set overrides in the PowerShell session before running pytest:

```powershell
$env:API_BASE_URL = "http://localhost:8000"
$env:API_TIMEOUT = "5.5"
.\.venv\Scripts\python.exe -m pytest tests/delete_requests -v --strict-markers
```

The example requires a running API with the same endpoints and response contract.
Trailing slashes on the base URL are removed. The URL must use HTTP or HTTPS and
have no query string or fragment. The timeout must be positive and finite;
invalid settings raise an error at startup. Requests uses this timeout for
connection and read waits, rather than as a total test duration limit.

Remove the overrides to return to the defaults:

```powershell
Remove-Item Env:API_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:API_TIMEOUT -ErrorAction SilentlyContinue
```

Settings come from the process environment; `.env` files are not loaded automatically.
See `documents/pytest_commands.txt` for more test selection and execution examples.

## Test Markers

Every API test uses `test`, exactly one HTTP-method marker (`get`, `post`, `put`,
`patch`, or `delete`), and exactly one outcome marker (`positive` or `negative`).
The HTTP-method marker identifies the behavior under test; fixture setup,
verification, and cleanup requests do not add extra method markers.

Use this decorator order: `test`, HTTP method, optional `smoke` or `sanity`,
outcome, then `parametrize`. Existing smoke and sanity selections are preserved.
The POST validation parameters retain their individual `xfail` marks.
All custom markers are registered in `pytest.ini`, which enables strict marker
checking by default to catch unregistered marker names.

```powershell
.\.venv\Scripts\python.exe -m pytest tests -m "delete and negative" -v
.\.venv\Scripts\python.exe -m pytest tests -m "(put or patch) and positive" -v
.\.venv\Scripts\python.exe -m pytest tests -m "smoke and post" --collect-only -q
```

## GET Test Coverage

Run the GET tests with the project's virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/get_requests/test_get_objects.py -v --strict-markers
```

The tests cover listing objects, retrieving one object, filtering by multiple IDs,
404 responses for nonexistent and negative IDs, and an empty result for a filter
that matches no objects. The empty-result case uses the `positive` marker because
the filter is valid and the collection correctly responds with 200 and an empty list.
All tests use `test` and either `positive` or `negative`; core retrieval and
not-found checks also use `sanity`. Markers are registered in `pytest.ini`.

The configured `/objects` endpoint is public. Missing authorization and forbidden
access (401/403) require protected endpoints and an authorization setup, so they
are not tested against this endpoint. See the [API documentation](https://restful-api.dev/).

A large client timeout only increases how long a request may wait; it does not
cause a server error. A tiny timeout depends on network timing and is unreliable
as a live API test. Deterministic timeout handling tests would need a controlled
delayed server and application code that handles timeouts; this project currently
calls `requests` directly. No artificial timeout or simulated access-error tests
are included.

## Planned Next Steps

- add project dependencies
- create request helper/client layer
- add pytest configuration
- implement CRUD tests for the `objects` resource
- introduce fixtures for created test objects
- add basic reporting and test execution documentation
