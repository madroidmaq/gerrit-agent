"""Gerrit REST API Client"""

import json
from typing import Any

import httpx

from gerrit_cli.client.models import Change, ChangeDetail, CommentInfo, ReviewInput, ReviewResult
from gerrit_cli.utils.exceptions import ApiError, AuthenticationError, NotFoundError


class GerritClient:
    """Gerrit REST API Client"""

    def __init__(self, base_url: str, username: str, password: str) -> None:
        """Initialize Gerrit Client

        Args:
            base_url: Gerrit Server URL
            username: Username
            password: Password or HTTP Token
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password

        # Create httpx client with Basic Auth
        self.client = httpx.Client(
            auth=(username, password),
            headers={"Content-Type": "application/json; charset=UTF-8"},
            timeout=30.0,
        )

    def __enter__(self) -> "GerritClient":
        """Context manager enter"""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit, close connection"""
        self.close()

    def close(self) -> None:
        """Close HTTP client"""
        self.client.close()

    def _make_request(
        self, method: str, endpoint: str, params: dict[str, Any] | None = None, data: Any = None
    ) -> Any:
        """Unified request handler

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (will auto prepend /a/)
            params: URL query params
            data: Request body data

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: Authentication failed
            NotFoundError: Resource not found
            ApiError: Other API errors
        """
        # Add /a/ prefix for authentication
        if not endpoint.startswith("/a/"):
            endpoint = f"/a/{endpoint.lstrip('/')}"

        url = f"{self.base_url}{endpoint}"

        try:
            # Send request
            if data is not None:
                json_data = json.dumps(data) if not isinstance(data, str) else data
                response = self.client.request(method, url, params=params, content=json_data)
            else:
                response = self.client.request(method, url, params=params)

            # Handle error status codes
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed, please check username and password")
            elif response.status_code == 404:
                raise NotFoundError(f"Resource not found: {endpoint}")
            elif response.status_code >= 400:
                raise ApiError(
                    f"API request failed: {response.status_code} {response.text}",
                    status_code=response.status_code,
                )

            # Parse response
            return self._parse_response(response)

        except httpx.RequestError as e:
            raise ApiError(f"Network request failed: {e}")

    def _parse_response(self, response: httpx.Response) -> Any:
        """Parse Gerrit API response

        Gerrit API response starts with )]}' prefix to prevent XSSI attacks, need to remove it before parsing

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON data (dict or list)
        """
        text = response.text

        # Remove Gerrit security prefix
        if text.startswith(")]}'\n"):
            text = text[5:]

        # Empty response
        if not text.strip():
            return {}

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ApiError(f"JSON parse failed: {e}")

    # ==================== Changes API ====================

    def list_changes(
        self, query: str = "status:open", options: list[str] | None = None, limit: int = 25
    ) -> list[Change]:
        """List changes

        Args:
            query: Query conditions (default: status:open)
            options: Return options list (e.g. CURRENT_REVISION, LABELS etc.)
            limit: Result limit

        Returns:
            List of Change objects
        """
        params: dict[str, Any] = {"q": query, "n": limit}

        # Add return options
        if options:
            for opt in options:
                params["o"] = opt

        data = self._make_request("GET", "/changes/", params=params)

        # Parse as Change object list
        return [Change.model_validate(item) for item in data]

    def get_change(self, change_id: str, options: list[str] | None = None) -> ChangeDetail:
        """Get details of a single change

        Args:
            change_id: Change ID (can be numeric ID, Change-Id or full path)
            options: Return options list

        Returns:
            ChangeDetail object
        """
        params = {}
        if options:
            for opt in options:
                params["o"] = opt

        data = self._make_request("GET", f"/changes/{change_id}", params=params)
        return ChangeDetail.model_validate(data)

    def get_change_comments(self, change_id: str) -> dict[str, list[CommentInfo]]:
        """Get all comments for a change

        Args:
            change_id: Change ID

        Returns:
            Map of file path to comment list
        """
        data = self._make_request("GET", f"/changes/{change_id}/comments")

        # Parse comments
        result: dict[str, list[CommentInfo]] = {}
        for file_path, comments in data.items():
            result[file_path] = [CommentInfo.model_validate(c) for c in comments]

        return result

    def get_change_detail(self, change_id: str) -> ChangeDetail:
        """Get change details (including messages and labels)

        Args:
            change_id: Change ID

        Returns:
            ChangeDetail object
        """
        return self.get_change(
            change_id, options=["CURRENT_REVISION", "MESSAGES", "DETAILED_LABELS", "DETAILED_ACCOUNTS"]
        )

    # ==================== Review API ====================

    def set_review(
        self, change_id: str, revision_id: str, review_input: ReviewInput
    ) -> ReviewResult:
        """Send review (score and comment)

        Args:
            change_id: Change ID
            revision_id: Revision ID (use "current" for current revision)
            review_input: Review input data

        Returns:
            ReviewResult object
        """
        data = review_input.model_dump(exclude_none=True)
        result = self._make_request(
            "POST", f"/changes/{change_id}/revisions/{revision_id}/review", data=data
        )
        return ReviewResult.model_validate(result)

    def add_comment(self, change_id: str, message: str) -> ReviewResult:
        """Simplified add comment interface

        Args:
            change_id: Change ID
            message: Comment content

        Returns:
            ReviewResult object
        """
        review_input = ReviewInput(message=message)
        return self.set_review(change_id, "current", review_input)

    # ==================== Files and Diffs API ====================

    def get_change_files(self, change_id: str, revision_id: str = "current") -> dict[str, Any]:
        """Get list of files changed in a revision

        Args:
            change_id: Change ID
            revision_id: Revision ID (default: "current")

        Returns:
            Dictionary mapping file paths to file info
            Format: {
                "file_path": {
                    "status": "M",  # M=Modified, A=Added, D=Deleted
                    "lines_inserted": 10,
                    "lines_deleted": 5,
                    "size_delta": 100,
                    "size": 1000
                }
            }
        """
        data = self._make_request("GET", f"/changes/{change_id}/revisions/{revision_id}/files/")
        return data

    def get_file_diff(
        self, change_id: str, file_path: str, revision_id: str = "current", context: int = 5
    ) -> dict[str, Any]:
        """Get diff for a specific file

        Args:
            change_id: Change ID
            file_path: File path
            revision_id: Revision ID (default: "current")
            context: Number of context lines (default: 5)

        Returns:
            Diff data in Gerrit format
        """
        from urllib.parse import quote

        # URL encode the file path
        encoded_path = quote(file_path, safe="")
        params = {"context": context}
        data = self._make_request(
            "GET",
            f"/changes/{change_id}/revisions/{revision_id}/files/{encoded_path}/diff",
            params=params,
        )
        return data

    def get_all_diffs(
        self, change_id: str, revision_id: str = "current", context: int = 5
    ) -> dict[str, Any]:
        """Get diffs for all files in a change

        Args:
            change_id: Change ID
            revision_id: Revision ID (default: "current")

        Returns:
            Dictionary mapping file paths to their diff data
        """
        files = self.get_change_files(change_id, revision_id)
        diffs = {}

        for file_path in files.keys():
            # Skip commit message and other special files
            if file_path in ["/COMMIT_MSG", "/MERGE_LIST"]:
                continue

            try:
                diffs[file_path] = self.get_file_diff(
                    change_id, file_path, revision_id, context=context
                )
            except (ApiError, NotFoundError):
                # Some files might not have diffs (e.g., binary files)
                continue

        return diffs
