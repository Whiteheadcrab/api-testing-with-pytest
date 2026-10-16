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
