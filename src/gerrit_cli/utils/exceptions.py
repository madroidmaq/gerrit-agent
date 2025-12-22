"""Custom exceptions"""

from typing import Optional


class GerritCliError(Exception):
    """Base CLI exception"""

    pass


class ConfigError(GerritCliError):
    """Configuration error"""

    pass


class ApiError(GerritCliError):
    """API request error"""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(ApiError):
    """Authentication error"""

    pass


class NotFoundError(ApiError):
    """Resource not found"""

    pass
