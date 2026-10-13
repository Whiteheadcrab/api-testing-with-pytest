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

## Planned Next Steps

- add project dependencies
- create request helper/client layer
- add pytest configuration
- implement CRUD tests for the `objects` resource
- introduce fixtures for created test objects
- add basic reporting and test execution documentation
