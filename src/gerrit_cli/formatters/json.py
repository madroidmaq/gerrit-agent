"""JSON Formatter"""

import json

from gerrit_cli.client.models import Change, ChangeDetail
from gerrit_cli.formatters.base import Formatter


class JsonFormatter(Formatter):
    """JSON formatter"""

    def format_changes(
        self, changes: list[Change], has_more: bool = False, limit: int | None = None
    ) -> str:
        """Format changes list as JSON

        Args:
            changes: List of Change objects

        Returns:
            JSON string
        """
        data = [change.model_dump(mode="json") for change in changes]
        return json.dumps(data, indent=2, ensure_ascii=False)

    def format_change_detail(self, change: ChangeDetail, show_comments: bool = False) -> str:
        """Format change detail as JSON

        Args:
            change: ChangeDetail object
            show_comments: Whether to show comments (JSON always includes all data)

        Returns:
            JSON string
        """
        data = change.model_dump(mode="json")
        return json.dumps(data, indent=2, ensure_ascii=False)
