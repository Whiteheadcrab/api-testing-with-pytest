# Base address comes from the environment configuration shared by all tests.
from config import BASE_URL


# Groups collection and individual-object endpoints in one place.
class ObjectsApiUrls:
    # Collection endpoint for listing, filtering, and creating objects.
    BASE = f"{BASE_URL}/objects"

    # No instance state is needed to build an endpoint from a string or integer ID.
    @staticmethod
    def object_by_id(object_id: str | int) -> str:
        # Individual-object endpoint used by GET, PUT, PATCH, and DELETE requests.
        return f"{ObjectsApiUrls.BASE}/{object_id}"


# Shared URL provider imported by the test modules.
OBJECTS_URLS = ObjectsApiUrls()
