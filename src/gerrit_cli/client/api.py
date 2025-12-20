"""Gerrit REST API 客户端"""

import json
from typing import Any

import httpx

from gerrit_cli.client.models import Change, ChangeDetail, CommentInfo, ReviewInput, ReviewResult
from gerrit_cli.utils.exceptions import ApiError, AuthenticationError, NotFoundError


class GerritClient:
    """Gerrit REST API 客户端"""

    def __init__(self, base_url: str, username: str, password: str) -> None:
        """初始化 Gerrit 客户端

        Args:
            base_url: Gerrit 服务器 URL
            username: 用户名
            password: 密码或 HTTP Token
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password

        # 创建 httpx 客户端，配置 Basic Auth
        self.client = httpx.Client(
            auth=(username, password),
            headers={"Content-Type": "application/json; charset=UTF-8"},
            timeout=30.0,
        )

    def __enter__(self) -> "GerritClient":
        """Context manager 入口"""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager 退出，关闭连接"""
        self.close()

    def close(self) -> None:
        """关闭 HTTP 客户端"""
        self.client.close()

    def _make_request(
        self, method: str, endpoint: str, params: dict[str, Any] | None = None, data: Any = None
    ) -> Any:
        """统一的请求处理方法

        Args:
            method: HTTP 方法（GET, POST, PUT, DELETE）
            endpoint: API 端点（会自动添加 /a/ 前缀）
            params: URL 查询参数
            data: 请求体数据

        Returns:
            解析后的 JSON 响应

        Raises:
            AuthenticationError: 认证失败
            NotFoundError: 资源不存在
            ApiError: 其他 API 错误
        """
        # 添加 /a/ 前缀用于认证
        if not endpoint.startswith("/a/"):
            endpoint = f"/a/{endpoint.lstrip('/')}"

        url = f"{self.base_url}{endpoint}"

        try:
            # 发送请求
            if data is not None:
                json_data = json.dumps(data) if not isinstance(data, str) else data
                response = self.client.request(method, url, params=params, content=json_data)
            else:
                response = self.client.request(method, url, params=params)

            # 处理错误状态码
            if response.status_code == 401:
                raise AuthenticationError("认证失败，请检查用户名和密码")
            elif response.status_code == 404:
                raise NotFoundError(f"资源不存在: {endpoint}")
            elif response.status_code >= 400:
                raise ApiError(
                    f"API 请求失败: {response.status_code} {response.text}",
                    status_code=response.status_code,
                )

            # 解析响应
            return self._parse_response(response)

        except httpx.RequestError as e:
            raise ApiError(f"网络请求失败: {e}")

    def _parse_response(self, response: httpx.Response) -> Any:
        """解析 Gerrit API 响应

        Gerrit API 响应以 )]}' 前缀开头以防止 XSSI 攻击，需要移除后再解析

        Args:
            response: HTTP 响应对象

        Returns:
            解析后的 JSON 数据（dict 或 list）
        """
        text = response.text

        # 移除 Gerrit 的安全前缀
        if text.startswith(")]}'\n"):
            text = text[5:]

        # 空响应
        if not text.strip():
            return {}

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ApiError(f"JSON 解析失败: {e}")

    # ==================== Changes API ====================

    def list_changes(
        self, query: str = "status:open", options: list[str] | None = None, limit: int = 25
    ) -> list[Change]:
        """查询 changes 列表

        Args:
            query: 查询条件（默认: status:open）
            options: 返回选项列表（如 CURRENT_REVISION, LABELS 等）
            limit: 返回结果数量限制

        Returns:
            Change 对象列表
        """
        params: dict[str, Any] = {"q": query, "n": limit}

        # 添加返回选项
        if options:
            for opt in options:
                params["o"] = opt

        data = self._make_request("GET", "/changes/", params=params)

        # 解析为 Change 对象列表
        return [Change.model_validate(item) for item in data]

    def get_change(self, change_id: str, options: list[str] | None = None) -> ChangeDetail:
        """获取单个 change 的详细信息

        Args:
            change_id: Change ID（可以是数字 ID、Change-Id 或完整路径）
            options: 返回选项列表

        Returns:
            ChangeDetail 对象
        """
        params = {}
        if options:
            for opt in options:
                params["o"] = opt

        data = self._make_request("GET", f"/changes/{change_id}", params=params)
        return ChangeDetail.model_validate(data)

    def get_change_comments(self, change_id: str) -> dict[str, list[CommentInfo]]:
        """获取 change 的所有评论

        Args:
            change_id: Change ID

        Returns:
            文件路径到评论列表的映射
        """
        data = self._make_request("GET", f"/changes/{change_id}/comments")

        # 解析评论
        result: dict[str, list[CommentInfo]] = {}
        for file_path, comments in data.items():
            result[file_path] = [CommentInfo.model_validate(c) for c in comments]

        return result

    def get_change_detail(self, change_id: str) -> ChangeDetail:
        """获取 change 的详细信息（包含消息和标签）

        Args:
            change_id: Change ID

        Returns:
            ChangeDetail 对象
        """
        return self.get_change(
            change_id, options=["CURRENT_REVISION", "MESSAGES", "DETAILED_LABELS"]
        )

    # ==================== Review API ====================

    def set_review(
        self, change_id: str, revision_id: str, review_input: ReviewInput
    ) -> ReviewResult:
        """发送 review（包含打分和评论）

        Args:
            change_id: Change ID
            revision_id: Revision ID（可以使用 "current" 表示当前 revision）
            review_input: Review 输入数据

        Returns:
            ReviewResult 对象
        """
        data = review_input.model_dump(exclude_none=True)
        result = self._make_request(
            "POST", f"/changes/{change_id}/revisions/{revision_id}/review", data=data
        )
        return ReviewResult.model_validate(result)

    def add_comment(self, change_id: str, message: str) -> ReviewResult:
        """简化的添加评论接口

        Args:
            change_id: Change ID
            message: 评论内容

        Returns:
            ReviewResult 对象
        """
        review_input = ReviewInput(message=message)
        return self.set_review(change_id, "current", review_input)
