"""Table Formatter"""

from datetime import datetime
from typing import Optional, Dict, Union, Any

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.rule import Rule

from gerrit_cli.client.models import Change, ChangeDetail
from gerrit_cli.formatters.base import Formatter
from gerrit_cli.utils.helpers import shorten_path


class Section:
    """统一的 Section 组件，用于格式化 title + divider + content

    提供一致的渲染方式，避免代码重复和不一致的格式化逻辑。
    """

    def __init__(self, title: str, content: Union[Text, str, Table]):
        """初始化 Section

        Args:
            title: Section 标题
            content: Section 内容（支持 Text、str 或 Table）
        """
        self.title = title
        self.content = content

    def render(self, console: Console) -> None:
        """统一的渲染方法

        渲染格式：
        1. 空行
        2. Title（bold cyan）
        3. Rule 分割线（dim）
        4. Content

        Args:
            console: Rich Console 对象
        """
        console.print()  # 添加空行
        console.print(f"[bold cyan]{self.title}[/bold cyan]")
        console.print(Rule(style="dim"))
        console.print(self.content)


class TableFormatter(Formatter):
    """Table formatter using rich"""

    def __init__(self) -> None:
        self.console = Console()

    def format_changes(
        self, changes: list[Change], has_more: bool = False, limit: Optional[int] = None
    ) -> str:
        """Format changes list as a table

        Args:
            changes: List of Change objects

        Returns:
            Formatted table string
        """
        if not changes:
            return "No changes found"

        # Build title
        title = f"Changes ({len(changes)} items)"
        if has_more:
            title += " [yellow](more available)[/yellow]"
        if limit:
            title += f" (limit: {limit})"
 
        table = Table(title=title)
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
        # Title
        title_text = Text()
        title_text.append(f"Change {change.display_id}: ", style="bold cyan")
        title_text.append(change.subject, style="bold white")

        # Basic Info content
        info_content = Text()
        info_content.append(f"Project: {change.project}\n")
        info_content.append(f"Branch: {change.branch}\n")
        info_content.append(f"Status: {change.status}\n")
        info_content.append(f"Owner: {change.owner.name if change.owner else 'Unknown'}\n")
        info_content.append(f"Created: {self._format_time(change.created)}\n")
        info_content.append(f"Updated: {self._format_time(change.updated)}\n")
        info_content.append(f"Changes: +{change.insertions}/-{change.deletions}\n")

        # Label Labels
        if change.labels:
            label_text = []
            for label_name, label_info in change.labels.items():
                value = label_info.value if label_info.value is not None else 0
                label_text.append(f"{label_name}: {value:+d}")
            info_content.append(f"Labels: {', '.join(label_text)}\n")

        info_section = self._format_section("Basic Info", info_content)

        # Message History
        sections = [info_section]
        if change.messages:
            messages_content = Text()
            for msg in change.messages[-5:]:  # Show only last 5 messages
                author_name = msg.author.name if msg.author else "Unknown"
                messages_content.append(f"[{self._format_time(msg.date)}] {author_name}:\n")
                messages_content.append(f"  {msg.message[:200]}\n\n")
            messages_section = self._format_section("Recent Messages", messages_content)
            sections.append(messages_section)

        # Capture Output - 使用统一的 Section.render() 方法
        with self.console.capture() as capture:
            self.console.print(title_text)
            for section in sections:
                section.render(self.console)

        return capture.get()

    def format_change_complete(
        self,
        change: ChangeDetail,
        files: Optional[Dict[str, Any]] = None,
        diffs: Optional[Dict[str, Any]] = None,
        comments: Optional[Dict[str, Any]] = None,
        show_parts: Optional[Dict[str, bool]] = None,
        context: int = 5,
    ) -> str:
        """Format complete change view (similar to tig show)

        Args:
            change: ChangeDetail object
            files: File list data
            diffs: Diff data
            comments: Comments data
            show_parts: Parts to display, e.g. {"metadata": True, "files": True, ...}
            context: Number of diff context lines (default: 5)

        Returns:
            Formatted string
        """
        if show_parts is None:
            # 默认显示元数据、文件、消息（不含 diff）
            show_parts = {
                "metadata": True,
                "files": True,
                "diff": False,
                "messages": True,
                "comments": False,
            }

        parts: list[Section] = []

        # ========== 元数据部分 ==========
        if show_parts.get("metadata", False):
            parts.append(self._render_metadata_panel(change))

        # ========== 文件列表部分 ==========
        if show_parts.get("files", False) and files:
            parts.append(self._render_files_panel(files, change))

        # ========== 评论部分 (提前到 FILES 之后) ==========
        if show_parts.get("comments", False) and comments:
            parts.append(self._render_comments_panel(comments))

        # ========== 消息历史部分 ==========
        if show_parts.get("messages", False) and change.messages:
            parts.append(self._render_messages_panel(change.messages))

        # ========== DIFF 部分 ==========
        if show_parts.get("diff", False) and diffs:
            parts.append(self._render_diffs_panel(diffs, context=context))

        # 合并所有部分 - 使用统一的 Section.render() 方法
        with self.console.capture() as capture:
            for section in parts:
                section.render(self.console)

        return capture.get()

    def _render_metadata_panel(self, change: ChangeDetail) -> Section:
        """Render metadata section"""
        # 标题
        title_text = f"Change {change.display_id}: {change.subject}  [{change.status}]"

        # 内容
        content = Text()
        content.append("Project: ", style="cyan")
        content.append(f"{change.project}\n")
        content.append("Branch:  ", style="cyan")
        content.append(f"{change.branch}\n")
        content.append("Owner:   ", style="cyan")
        content.append(f"{change.owner.name if change.owner else 'Unknown'}\n")
        content.append("Created: ", style="cyan")
        content.append(f"{self._format_time(change.created)}\n", style="dim")
        content.append("Updated: ", style="cyan")
        content.append(f"{self._format_time(change.updated)}\n", style="dim")
        content.append("Changes: ", style="cyan")
        content.append(f"+{change.insertions}/-{change.deletions}\n", style="green")

        # Labels
        if change.labels:
            content.append("\nLabels:\n", style="bold cyan")
            for label_name, label_info in change.labels.items():
                value = label_info.value if label_info.value is not None else 0
                color = "green" if value > 0 else "red" if value < 0 else "white"
                content.append(f"  • {label_name}: ", style="white")
                content.append(f"{value:+d}\n", style=color)

        return self._format_section(title_text, content)

    def _render_files_panel(
        self, files: Dict[str, Any], change: ChangeDetail
    ) -> Section:
        """Render files list section

        Returns tuple of (title, divider_char, table) for caller to print
        """
        file_count = len([f for f in files.keys() if f not in ["/COMMIT_MSG", "/MERGE_LIST"]])
        title = f"FILES CHANGED ({file_count} files, +{change.insertions}/-{change.deletions})"

        # Calculate available width for the file path
        # Console width - borders/padding (4) - Status (3) - Changes (15) - spacings
        # Default Console width is 80 if not detectable
        available_width = self.console.width - 26
        if available_width < 20:
            available_width = 20  # Minimum safeguard

        # 创建表格
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Status", style="yellow", width=3)
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Changes", style="blue", justify="right", width=15)

        for file_path, file_info in files.items():
            # 跳过特殊文件
            if file_path in ["/COMMIT_MSG", "/MERGE_LIST"]:
                continue

            # 文件状态
            status = file_info.get("status", "M")
            insertions = file_info.get("lines_inserted", 0)
            deletions = file_info.get("lines_deleted", 0)

            changes_str = f"+{insertions} -{deletions}"

            display_path = shorten_path(file_path, max_length=available_width)
            table.add_row(status, display_path, changes_str)

        return self._format_section(title, table)

    def _render_diffs_panel(
        self, diffs: Dict[str, Any], context: int = 5
    ) -> Section:
        """Render diff section

        Args:
            diffs: Diff data dictionary
            context: Number of context lines for changes (default: 5)
        """
        content = Text()

        for file_path, diff_data in diffs.items():
            # 文件头
            content.append(f"\n{'=' * 80}\n", style="dim")
            content.append(f"diff --git a/{file_path} b/{file_path}\n", style="bold white")
            content.append(f"{'=' * 80}\n", style="dim")

            # 转换 Gerrit diff 为 unified diff 格式，限制上下文行数
            unified_diff = self._convert_gerrit_diff_to_unified(diff_data, context=context)

            # 语法高亮显示 diff
            for line in unified_diff.split("\n"):
                if line.startswith("@@"):
                    content.append(line + "\n", style="cyan bold")
                elif line.startswith("+"):
                    content.append(line + "\n", style="green")
                elif line.startswith("-"):
                    content.append(line + "\n", style="red")
                else:
                    content.append(line + "\n", style="white")

        return self._format_section("DIFF", content)

    def _render_messages_panel(self, messages: list[Any]) -> Section:
        """Render messages history section"""
        content = Text()

        # 只显示最近 8 条消息（增加一些可见度）
        recent_messages = messages[-8:] if len(messages) > 8 else messages

        for msg in recent_messages:
            author_name = msg.author.name if msg.author else "Unknown"
            time_str = self._format_time(msg.date)

            content.append(f"[{time_str}] ", style="dim")
            content.append(f"{author_name}:", style="bold cyan")

            # 标记包含评论的消息
            if "(1 comment)" in msg.message or " comments)" in msg.message:
                 content.append(" 💬", style="yellow")

            content.append("\n")

            # 处理消息内容（可能有多行）
            for line in msg.message.split("\n"):
                if line.strip():
                    content.append(f"  {line}\n")

            content.append("\n")

        title = f"RECENT MESSAGES ({len(messages)})"
        return self._format_section(title, content)

    def _render_comments_panel(
        self, comments: Dict[str, Any]
    ) -> Section:
        """Render comments section, grouped by file, line number and author"""
        content = Text()

        if not comments:
            no_comments_text = Text("No inline comments")
            return self._format_section("INLINE COMMENTS", no_comments_text)

        file_count = 0
        comment_count = 0

        # 计算可用宽度用于缩短路径
        available_width = self.console.width - 15
        if available_width < 20:
            available_width = 20

        for file_path, comment_list in comments.items():
            if not comment_list:
                continue

            file_count += 1
            comment_count += len(comment_list)

            # 缩短文件路径，并作为文件头展示
            display_path = shorten_path(file_path, max_length=available_width)
            content.append(f"\n{display_path}\n", style="bold magenta underline")

            # 按行号对评论进行预分组
            line_groups: Dict[Any, list[Any]] = {}
            for comment in comment_list:
                line = comment.line if comment.line else "File"
                if line not in line_groups:
                    line_groups[line] = []
                line_groups[line].append(comment)

            # 按行号排序并展示
            sorted_lines = sorted(
                line_groups.keys(),
                key=lambda x: (0, int(x)) if isinstance(x, int) or (isinstance(x, str) and x.isdigit()) else (1, x)
            )

            for line in sorted_lines:
                # 行号标题（缩进一层）
                line_text = f"Line {line}" if isinstance(line, int) or str(line).isdigit() else line
                content.append(f"  {line_text}:\n", style="bold yellow")

                # 在该行内按作者归并
                author_groups: Dict[str, list[Any]] = {}
                for comment in line_groups[line]:
                    author = comment.author.name if comment.author else "Unknown"
                    if author not in author_groups:
                        author_groups[author] = []
                    author_groups[author].append(comment)

                for author, author_comments in author_groups.items():
                    # 取最后一条评论的时间
                    last_updated = author_comments[-1].updated
                    time_str = f" [{self._format_time(last_updated)}]" if last_updated else ""

                    # 展示作者（缩进两层）
                    content.append(f"    {author}{time_str}:\n", style="bold cyan")

                    # 展示该作者的所有评论内容（缩进三层）
                    for comment in author_comments:
                        lines = comment.message.split("\n")
                        for i, line in enumerate(lines):
                            if line.strip() or i < len(lines) - 1:
                                content.append(f"      {line}\n")
                    content.append("\n")

        title = f"INLINE COMMENTS ({comment_count} comments in {file_count} files)"
        return self._format_section(title, content)

    def _convert_gerrit_diff_to_unified(
        self, gerrit_diff: Dict[str, Any], context: int = 5
    ) -> str:
        """Convert Gerrit diff format to unified diff format with limited context lines

        Gerrit diff format:
        {
            "content": [
                {"ab": ["context line"]},  # Context lines
                {"a": ["old line"], "b": ["new line"]},  # Modified lines
                ...
            ]
        }

        Args:
            gerrit_diff: Gerrit diff data
            context: Number of context lines for changes (lines on each side)

        Returns:
            Unified diff format string
        """
        lines = []
        content_sections = gerrit_diff.get("content", [])

        for i, section in enumerate(content_sections):
            if "ab" in section:
                # 上下文行（未修改）
                ab_lines = section["ab"]
                total_lines = len(ab_lines)

                # 判断这个 ab section 的位置：是否在改动前后
                is_before_change = i < len(content_sections) - 1 and self._is_change_section(
                    content_sections[i + 1]
                )
                is_after_change = i > 0 and self._is_change_section(content_sections[i - 1])

                if is_before_change and is_after_change:
                    # 在两个改动之间：显示前一个改动的后 context 行 + 后一个改动的前 context 行
                    if total_lines > context * 2:
                        # 只保留前 context 行和后 context 行
                        for line in ab_lines[:context]:
                            lines.append(f" {line}")
                        lines.append(f"@@ ... skipped {total_lines - context * 2} lines ... @@")
                        for line in ab_lines[-context:]:
                            lines.append(f" {line}")
                    else:
                        # 全部显示
                        for line in ab_lines:
                            lines.append(f" {line}")
                elif is_before_change:
                    # 在改动之前：只显示最后 context 行
                    if total_lines > context:
                        lines.append(f"@@ ... skipped {total_lines - context} lines ... @@")
                        for line in ab_lines[-context:]:
                            lines.append(f" {line}")
                    else:
                        for line in ab_lines:
                            lines.append(f" {line}")
                elif is_after_change:
                    # 在改动之后：只显示前 context 行
                    if total_lines > context:
                        for line in ab_lines[:context]:
                            lines.append(f" {line}")
                        lines.append(f"@@ ... skipped {total_lines - context} lines ... @@")
                    else:
                        for line in ab_lines:
                            lines.append(f" {line}")
                else:
                    # 孤立的 ab section（不在任何改动附近）：完全跳过或显示部分
                    if total_lines > context * 2:
                        lines.append(f"@@ ... skipped {total_lines} lines ... @@")
                    else:
                        for line in ab_lines:
                            lines.append(f" {line}")

            elif "skip" in section:
                # Gerrit 已经提供的跳过信息
                lines.append(f"@@ ... skipped {section['skip']} lines ... @@")
            elif "a" in section and "b" in section:
                # 修改的行（先删除后添加）
                for line in section["a"]:
                    lines.append(f"-{line}")
                for line in section["b"]:
                    lines.append(f"+{line}")
            elif "a" in section:
                # 仅删除的行
                for line in section["a"]:
                    lines.append(f"-{line}")
            elif "b" in section:
                # 仅添加的行
                for line in section["b"]:
                    lines.append(f"+{line}")

        return "\n".join(lines)

    def _is_change_section(self, section: Dict[str, Any]) -> bool:
        """Check if a section contains changes (not pure context)"""
        return "a" in section or "b" in section

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

    def _format_section(
        self, title: str, content: Union[Text, str, Table, None] = None, divider_char: str = "─"
    ) -> Section:
        """Format a section with title + divider + content (LLM-friendly format)

        使用统一的 Section 组件，确保所有部分使用一致的格式化方式。

        Args:
            title: Section title
            content: Section content (Text, str, Table, or None)
            divider_char: Character used for divider line (deprecated, kept for compatibility)

        Returns:
            Section object with unified rendering logic
        """
        # 如果 content 为 None，创建空的 Text
        if content is None:
            content = Text()

        return Section(title, content)
