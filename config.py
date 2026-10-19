"""Read shared API settings from the process environment at startup."""

import os
from math import isfinite
from urllib.parse import urlsplit


# Keep existing behavior when no environment overrides are provided.
BASE_URL = os.getenv("API_BASE_URL", "https://api.restful-api.dev").strip().rstrip("/")
_parsed_url = urlsplit(BASE_URL)
if _parsed_url.scheme not in ("http", "https") or not _parsed_url.hostname:
    raise ValueError("API_BASE_URL must be an absolute HTTP or HTTPS URL.")
if _parsed_url.query or _parsed_url.fragment:
    raise ValueError("API_BASE_URL must not include a query string or fragment.")

# requests accepts fractional seconds, but a timeout must be positive and finite.
try:
    REQUEST_TIMEOUT = float(os.getenv("API_TIMEOUT", "10"))
except ValueError as error:
    raise ValueError("API_TIMEOUT must be a positive, finite number of seconds.") from error
if not isfinite(REQUEST_TIMEOUT) or REQUEST_TIMEOUT <= 0:
    raise ValueError("API_TIMEOUT must be a positive, finite number of seconds.")
