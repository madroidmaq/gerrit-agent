"""Table Formatter"""

from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from gerrit_cli.client.models import Change, ChangeDetail
from gerrit_cli.formatters.base import Formatter


class TableFormatter(Formatter):
    """Table formatter using rich"""

    def __init__(self) -> None:
        self.console = Console()

    def format_changes(self, changes: list[Change]) -> str:
        """Format changes list as a table

        Args:
            changes: List of Change objects

        Returns:
            Formatted table string
        """
        if not changes:
            return "No changes found"

        table = Table(title=f"Changes ({len(changes)} items)")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Subject", style="white")
        table.add_column("Owner", style="green")
        table.add_column("Project", style="magenta")
        table.add_column("Status", style="yellow")
        table.add_column("+/-", style="blue", no_wrap=True)
        table.add_column("Updated", style="dim")

        for change in changes:
            owner_name = ""
            if change.owner:
                owner_name = change.owner.name or change.owner.username or ""

            # Format insertions/deletions
            changes_text = f"+{change.insertions}/-{change.deletions}"

            # Format updated time
            updated = self._format_time(change.updated)

            table.add_row(
                change.display_id,
                change.subject[:80],  # Limit length
                owner_name,
                change.project,
                change.status,
                changes_text,
                updated,
            )

        # Capture console output
        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def format_change_detail(self, change: ChangeDetail, show_comments: bool = False) -> str:
        """Format change details

        Args:
            change: ChangeDetail object
            show_comments: Whether to show comments (not implemented yet)

        Returns:
            Formatted detail string
        """
        output_parts = []

        # Title
        title = Text()
        title.append(f"Change {change.display_id}: ", style="bold cyan")
        title.append(change.subject, style="bold white")

        # Basic Info Panel
        info_lines = [
            f"Project: {change.project}",
            f"Branch: {change.branch}",
            f"Status: {change.status}",
            f"Owner: {change.owner.name if change.owner else 'Unknown'}",
            f"Created: {self._format_time(change.created)}",
            f"Updated: {self._format_time(change.updated)}",
            f"Changes: +{change.insertions}/-{change.deletions}",
        ]

        # Label Labels
        if change.labels:
            label_text = []
            for label_name, label_info in change.labels.items():
                value = label_info.value if label_info.value is not None else 0
                label_text.append(f"{label_name}: {value:+d}")
            info_lines.append(f"Labels: {', '.join(label_text)}")

        info_panel = Panel("\n".join(info_lines), title="Basic Info", border_style="cyan")

        # Message History
        messages_text = []
        if change.messages:
            for msg in change.messages[-5:]:  # Show only last 5 messages
                author_name = msg.author.name if msg.author else "Unknown"
                messages_text.append(
                    f"[{self._format_time(msg.date)}] {author_name}:\n  {msg.message[:200]}"
                )

        # Capture Output
        with self.console.capture() as capture:
            self.console.print(title)
            self.console.print(info_panel)

            if messages_text:
                messages_panel = Panel(
                    "\n\n".join(messages_text), title="Recent Messages", border_style="yellow"
                )
                self.console.print(messages_panel)

        return capture.get()

    def _format_time(self, time_str: str) -> str:
        """Format time string

        Args:
            time_str: Gerrit time string (Format: 2025-01-01 00:00:00.000000000)

        Returns:
            Formatted time string
        """
        try:
            # Gerrit Time Format: 2025-01-01 00:00:00.000000000
            # Remove nanoseconds
            if "." in time_str:
                time_str = time_str.split(".")[0]

            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            # Calculate time difference
            now = datetime.now()
            diff = now - dt

            if diff.days > 365:
                return f"{diff.days // 365} years ago"
            elif diff.days > 30:
                return f"{diff.days // 30} months ago"
            elif diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600} hours ago"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60} minutes ago"
            else:
                return "Just now"
        except Exception:
            return time_str
