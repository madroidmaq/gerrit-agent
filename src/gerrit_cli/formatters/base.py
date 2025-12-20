"""格式化器基类"""

from abc import ABC, abstractmethod

from gerrit_cli.client.models import Change, ChangeDetail


class Formatter(ABC):
    """格式化器抽象基类"""

    @abstractmethod
    def format_changes(self, changes: list[Change]) -> str:
        """格式化 changes 列表

        Args:
            changes: Change 对象列表

        Returns:
            格式化后的字符串
        """
        pass

    @abstractmethod
    def format_change_detail(self, change: ChangeDetail, show_comments: bool = False) -> str:
        """格式化 change 详情

        Args:
            change: ChangeDetail 对象
            show_comments: 是否显示评论

        Returns:
            格式化后的字符串
        """
        pass
