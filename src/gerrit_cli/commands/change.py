"""Change 命令组"""

import sys

import click

from gerrit_cli.client.api import GerritClient
from gerrit_cli.formatters import get_formatter
from gerrit_cli.utils.exceptions import GerritCliError


@click.group()
def change() -> None:
    """Change 相关命令"""
    pass


@change.command()
@click.option("-q", "--query", default="status:open", help="查询条件（默认: status:open）")
@click.option("-n", "--limit", default=25, type=int, help="返回结果数量（默认: 25）")
@click.option("-o", "--owner", help="按所有者筛选（使用 'me' 表示当前用户）")
@click.option("-p", "--project", help="按项目筛选")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="输出格式",
)
@click.pass_context
def list(
    ctx: click.Context,
    query: str,
    limit: int,
    owner: str | None,
    project: str | None,
    output_format: str,
) -> None:
    """列出 changes

    示例:
        gerrit change list
        gerrit change list -q "status:merged"
        gerrit change list --owner me
        gerrit change list --project myproject --format json
    """
    config = ctx.obj["config"]

    try:
        # 构建查询条件
        query_parts = [query]

        if owner:
            if owner == "me":
                query_parts.append(f"owner:{config.username}")
            else:
                query_parts.append(f"owner:{owner}")

        if project:
            query_parts.append(f"project:{project}")

        final_query = " ".join(query_parts)

        # 调用 API
        with GerritClient(config.url, config.username, config.password) as client:
            changes = client.list_changes(
                query=final_query, options=["CURRENT_REVISION", "LABELS"], limit=limit
            )

        # 格式化输出
        formatter = get_formatter(output_format)
        output = formatter.format_changes(changes)
        click.echo(output)

    except GerritCliError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@change.command()
@click.argument("change_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="输出格式",
)
@click.option("--comments", is_flag=True, help="显示评论")
@click.option("--messages", is_flag=True, help="显示消息历史（默认显示）")
@click.option("--files", is_flag=True, help="显示文件列表")
@click.pass_context
def view(
    ctx: click.Context,
    change_id: str,
    output_format: str,
    comments: bool,
    messages: bool,
    files: bool,
) -> None:
    """查看 change 详情

    CHANGE_ID 可以是数字 ID、Change-Id 或完整路径

    示例:
        gerrit change view 12345
        gerrit change view I1234567890abcdef
        gerrit change view 12345 --comments
        gerrit change view 12345 --format json
    """
    config = ctx.obj["config"]

    try:
        # 调用 API 获取详情
        with GerritClient(config.url, config.username, config.password) as client:
            change = client.get_change_detail(change_id)

            # 如果需要显示评论
            if comments:
                comments_data = client.get_change_comments(change_id)
                # TODO: 将评论添加到输出中

        # 格式化输出
        formatter = get_formatter(output_format)
        output = formatter.format_change_detail(change, show_comments=comments)
        click.echo(output)

    except GerritCliError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@change.command()
@click.argument("change_id")
@click.option("-m", "--message", help="评论内容")
@click.option("-f", "--file", "file_path", type=click.Path(exists=True), help="从文件读取评论内容")
@click.option("--draft", is_flag=True, help="保存为草稿")
@click.pass_context
def comment(
    ctx: click.Context,
    change_id: str,
    message: str | None,
    file_path: str | None,
    draft: bool,
) -> None:
    """添加评论到 change

    示例:
        gerrit change comment 12345 -m "LGTM"
        gerrit change comment 12345 -f comment.txt
    """
    config = ctx.obj["config"]

    try:
        # 获取评论内容
        if message:
            comment_text = message
        elif file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                comment_text = f.read()
        else:
            click.echo("错误: 必须提供 -m 或 -f 选项", err=True)
            sys.exit(1)

        # 调用 API
        with GerritClient(config.url, config.username, config.password) as client:
            if draft:
                # TODO: 实现草稿评论
                click.echo("草稿功能暂未实现", err=True)
                sys.exit(1)
            else:
                result = client.add_comment(change_id, comment_text)
                click.echo(f"✓ 评论已添加到 Change {change_id}", err=False)

    except GerritCliError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
