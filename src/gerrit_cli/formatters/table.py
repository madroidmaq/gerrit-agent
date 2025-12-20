"""表格格式化器"""

from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from gerrit_cli.client.models import Change, ChangeDetail
from gerrit_cli.formatters.base import Formatter


class TableFormatter(Formatter):
    """使用 rich 的表格格式化器"""

    def __init__(self) -> None:
        self.console = Console()

    def format_changes(self, changes: list[Change]) -> str:
        """格式化 changes 列表为表格

        Args:
            changes: Change 对象列表

        Returns:
            格式化后的表格字符串
        """
        if not changes:
            return "没有找到 changes"

        table = Table(title=f"Changes ({len(changes)} 条)")
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

            # 格式化插入/删除行数
            changes_text = f"+{change.insertions}/-{change.deletions}"

            # 格式化更新时间
            updated = self._format_time(change.updated)

            table.add_row(
                change.display_id,
                change.subject[:80],  # 限制长度
                owner_name,
                change.project,
                change.status,
                changes_text,
                updated,
            )

        # 捕获 console 输出
        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def format_change_detail(self, change: ChangeDetail, show_comments: bool = False) -> str:
        """格式化 change 详情

        Args:
            change: ChangeDetail 对象
            show_comments: 是否显示评论（暂未实现）

        Returns:
            格式化后的详情字符串
        """
        output_parts = []

        # 标题
        title = Text()
        title.append(f"Change {change.display_id}: ", style="bold cyan")
        title.append(change.subject, style="bold white")

        # 基本信息面板
        info_lines = [
            f"Project: {change.project}",
            f"Branch: {change.branch}",
            f"Status: {change.status}",
            f"Owner: {change.owner.name if change.owner else 'Unknown'}",
            f"Created: {self._format_time(change.created)}",
            f"Updated: {self._format_time(change.updated)}",
            f"Changes: +{change.insertions}/-{change.deletions}",
        ]

        # 标签信息
        if change.labels:
            label_text = []
            for label_name, label_info in change.labels.items():
                value = label_info.value if label_info.value is not None else 0
                label_text.append(f"{label_name}: {value:+d}")
            info_lines.append(f"Labels: {', '.join(label_text)}")

        info_panel = Panel("\n".join(info_lines), title="基本信息", border_style="cyan")

        # 消息历史
        messages_text = []
        if change.messages:
            for msg in change.messages[-5:]:  # 只显示最近 5 条消息
                author_name = msg.author.name if msg.author else "Unknown"
                messages_text.append(
                    f"[{self._format_time(msg.date)}] {author_name}:\n  {msg.message[:200]}"
                )

        # 捕获输出
        with self.console.capture() as capture:
            self.console.print(title)
            self.console.print(info_panel)

            if messages_text:
                messages_panel = Panel(
                    "\n\n".join(messages_text), title="最近消息", border_style="yellow"
                )
                self.console.print(messages_panel)

        return capture.get()

    def _format_time(self, time_str: str) -> str:
        """格式化时间字符串

        Args:
            time_str: Gerrit 时间字符串（格式：2025-01-01 00:00:00.000000000）

        Returns:
            格式化后的时间字符串
        """
        try:
            # Gerrit 时间格式：2025-01-01 00:00:00.000000000
            # 移除纳秒部分
            if "." in time_str:
                time_str = time_str.split(".")[0]

            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            # 计算时间差
            now = datetime.now()
            diff = now - dt

            if diff.days > 365:
                return f"{diff.days // 365}年前"
            elif diff.days > 30:
                return f"{diff.days // 30}月前"
            elif diff.days > 0:
                return f"{diff.days}天前"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600}小时前"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60}分钟前"
            else:
                return "刚刚"
        except Exception:
            return time_str
