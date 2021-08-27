"""Define custom exceptions for the package."""

from requests.exceptions import RequestException


class ApiException(RequestException):
    """API-call related exceptions."""


class ThresholdException(ApiException):
    """One of the API's thresholds was exceeded."""
