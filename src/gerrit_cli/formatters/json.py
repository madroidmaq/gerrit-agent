"""JSON 格式化器"""

import json

from gerrit_cli.client.models import Change, ChangeDetail
from gerrit_cli.formatters.base import Formatter


class JsonFormatter(Formatter):
    """JSON 格式化器"""

    def format_changes(self, changes: list[Change]) -> str:
        """格式化 changes 列表为 JSON

        Args:
            changes: Change 对象列表

        Returns:
            JSON 字符串
        """
        data = [change.model_dump(mode="json") for change in changes]
        return json.dumps(data, indent=2, ensure_ascii=False)

    def format_change_detail(self, change: ChangeDetail, show_comments: bool = False) -> str:
        """格式化 change 详情为 JSON

        Args:
            change: ChangeDetail 对象
            show_comments: 是否显示评论（JSON 格式总是包含所有数据）

        Returns:
            JSON 字符串
        """
        data = change.model_dump(mode="json")
        return json.dumps(data, indent=2, ensure_ascii=False)
