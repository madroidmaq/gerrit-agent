"""Formatter Base Class"""

from abc import ABC, abstractmethod

from gerrit_cli.client.models import Change, ChangeDetail


class Formatter(ABC):
    """Abstract base class for formatters"""

    @abstractmethod
    def format_changes(
        self, changes: list[Change], has_more: bool = False, limit: int | None = None
    ) -> str:
        """Format changes list

        Args:
            changes: List of Change objects

        Returns:
            Formatted string
        """
        pass

    @abstractmethod
    def format_change_detail(self, change: ChangeDetail, show_comments: bool = False) -> str:
        """Format change details

        Args:
            change: ChangeDetail object
            show_comments: Whether to show comments

        Returns:
            Formatted string
        """
        pass
