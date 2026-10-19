# POST coverage for successful creation and invalid request payloads.

from pytest import mark, param

# The shared post_object fixture registers cleanup for every successful creation.

# Every test in this module calls a running API and requires explicit opt-in.
pytestmark = mark.live

# Markers select the API operation and outcome; parametrization runs each input separately.


# Verifies that creation returns the submitted fields and a generated ID.
@mark.test
@mark.post
@mark.positive
def test_post_object_creates_new_object(post_object):
    payload = {
        "name": "QA Automation Test Object",
        "data": {
            "created_by": "pytest",
            "request_type": "post",
        },
    }

    response = post_object(payload)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["name"] == payload["name"]
    assert response_body["data"] == payload["data"]
    assert response_body["id"]


# Each parameter retains its own expected-failure reason for unsupported validation.
@mark.test
@mark.post
@mark.negative
@mark.parametrize(
    "payload",
    [
        param(
            {"data": {"created_by": "pytest", "request_type": "post"}},
            marks=mark.xfail(reason="API currently accepts object creation without a name."),
            id="missing-name",
        ),
        param(
            {"name": "QA Automation Invalid Data Object", "data": "not-an-object"},
            marks=mark.xfail(reason="API currently accepts non-object data values."),
            id="invalid-data-format",
        ),
    ],
)
def test_post_object_creation_rejects_invalid_fields(payload, post_object):
    response = post_object(payload)

    assert response.status_code == 400


# Checks that an array payload is rejected because the endpoint expects a JSON object.
@mark.test
@mark.post
@mark.negative
def test_post_object_creation_fails_when_payload_schema_is_incorrect(post_object):
    payload = ["not", "a", "valid", "object", "payload"]

    response = post_object(payload)
    response_body = response.json()

    assert response.status_code == 400
    assert response_body["error"] == "Invalid request body"
