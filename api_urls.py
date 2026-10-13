BASE_URL = "https://api.restful-api.dev"


class ObjectsApiUrls:
    BASE = f"{BASE_URL}/objects"

    @staticmethod
    def object_by_id(object_id: str | int) -> str:
        return f"{ObjectsApiUrls.BASE}/{object_id}"


OBJECTS_URLS = ObjectsApiUrls()
