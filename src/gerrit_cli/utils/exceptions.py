"""自定义异常类"""


class GerritCliError(Exception):
    """CLI 基础异常"""

    pass


class ConfigError(GerritCliError):
    """配置错误"""

    pass


class ApiError(GerritCliError):
    """API 请求错误"""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(ApiError):
    """认证错误"""

    pass


class NotFoundError(ApiError):
    """资源不存在"""

    pass
