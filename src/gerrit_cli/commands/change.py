"""Change 命令组"""

import sys

import click

from gerrit_cli.client.api import GerritClient
from gerrit_cli.formatters import get_formatter
from gerrit_cli.utils.exceptions import GerritCliError
from gerrit_cli.utils.helpers import (
    branch_exists,
    check_git_repository,
    check_remote_exists,
    check_working_directory_clean,
    checkout_branch,
    checkout_fetch_head,
    delete_branch,
    fetch_change_ref,
    get_current_branch,
    get_git_remote_url,
    get_repo_root,
    stash_changes,
)


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


@change.command()
@click.argument("change_id")
@click.option("-b", "--branch", help="要创建的分支名称（默认: review/change-{change_id}）")
@click.option("--force", is_flag=True, help="如果分支已存在，强制删除并重新创建")
@click.option("--no-checkout", is_flag=True, help="只拉取不切换（保持在当前分支）")
@click.option(
    "--stash/--no-stash",
    default=None,
    help="当有未提交的修改时，是否自动 stash（默认会询问）",
)
@click.pass_context
def fetch(
    ctx: click.Context,
    change_id: str,
    branch: str | None,
    force: bool,
    no_checkout: bool,
    stash: bool | None,
) -> None:
    """拉取 change 到本地分支

    这个命令会从 Gerrit 拉取指定的 change 到本地，并创建一个新分支。
    如果工作区有未提交的修改，会提示你如何处理。

    CHANGE_ID 可以是数字 ID、Change-Id 或完整路径

    示例:
        # 拉取 change 12345 到新分支
        gerrit change fetch 12345

        # 指定分支名称
        gerrit change fetch 12345 -b my-review-branch

        # 如果分支已存在，强制重新创建
        gerrit change fetch 12345 --force

        # 只拉取不切换分支
        gerrit change fetch 12345 --no-checkout

        # 自动 stash 未提交的修改
        gerrit change fetch 12345 --stash
    """
    config = ctx.obj["config"]

    try:
        # 1. 检查是否在 Git 仓库中
        if not check_git_repository():
            click.echo("错误: 当前目录不是 Git 仓库", err=True)
            click.echo()
            click.echo("请先 cd 到 Gerrit 项目的 Git 仓库目录中，然后再运行此命令。", err=True)
            click.echo()
            click.echo("示例:")
            click.echo("  cd /path/to/your/gerrit/project")
            click.echo("  gerrit change fetch 12345")
            sys.exit(1)

        # 2. 从 Gerrit 获取 change 信息
        click.echo(f"正在获取 Change {change_id} 的信息...")
        with GerritClient(config.url, config.username, config.password) as client:
            change = client.get_change(change_id, options=["CURRENT_REVISION", "DOWNLOAD_COMMANDS"])

        # 3. 验证当前仓库是否匹配项目
        repo_root = get_repo_root()
        if repo_root:
            click.echo(f"当前仓库: {repo_root}")

        # 检查 remote 是否存在
        if not check_remote_exists("origin"):
            click.echo()
            click.echo("警告: 当前 Git 仓库没有配置 'origin' remote", err=True)
            click.echo("fetch 操作可能会失败。", err=True)
            click.echo()

            if not click.confirm("是否继续？", default=False):
                click.echo("操作已取消")
                sys.exit(0)
        else:
            # 获取 remote URL 并提示用户
            remote_url = get_git_remote_url("origin")
            if remote_url:
                click.echo(f"Remote URL: {remote_url}")

                # 简单检查：remote URL 中是否包含项目名称
                # 注意：这只是一个简单的启发式检查，不是完全可靠的
                if change.project not in remote_url:
                    click.echo()
                    click.echo(f"⚠️  警告: 当前仓库的 remote URL 似乎与 Change 的项目不匹配", err=True)
                    click.echo(f"   Change 项目: {change.project}", err=True)
                    click.echo(f"   Remote URL: {remote_url}", err=True)
                    click.echo()
                    click.echo("可能的原因:")
                    click.echo("  1. 你在错误的 Git 仓库中运行此命令")
                    click.echo(f"  2. 你需要 cd 到 '{change.project}' 项目的目录")
                    click.echo()

                    if not click.confirm("是否仍要继续 fetch？", default=False):
                        click.echo("操作已取消")
                        click.echo()
                        click.echo("建议:")
                        click.echo(f"  1. 找到 {change.project} 项目的 Git 仓库目录")
                        click.echo("  2. cd 到该目录")
                        click.echo(f"  3. 再次运行: gerrit change fetch {change_id}")
                        sys.exit(0)

        # 4. 验证 change 信息
        if not change.current_revision:
            click.echo("错误: 无法获取 change 的当前 revision", err=True)
            sys.exit(1)

        click.echo()

        # 5. 获取 ref spec
        # Gerrit ref 格式: refs/changes/[last 2 digits]/[change number]/[patch set number]
        change_number = change.number
        last_two = change_number % 100
        ref_spec = f"refs/changes/{last_two:02d}/{change_number}/1"

        click.echo(f"Change: {change.subject}")
        click.echo(f"Project: {change.project}")
        click.echo(f"Branch: {change.branch}")
        click.echo(f"Owner: {change.owner.name if change.owner else 'Unknown'}")
        click.echo(f"Ref: {ref_spec}")
        click.echo()

        # 6. 确定分支名称
        if branch is None:
            branch_name = f"review/change-{change_number}"
        else:
            branch_name = branch

        # 7. 检查分支是否已存在
        if branch_exists(branch_name):
            if force:
                click.echo(f"警告: 分支 '{branch_name}' 已存在，正在删除...")
                current = get_current_branch()
                if current == branch_name:
                    click.echo("错误: 无法删除当前所在的分支，请先切换到其他分支", err=True)
                    sys.exit(1)
                success, msg = delete_branch(branch_name, force=True)
                if not success:
                    click.echo(f"错误: {msg}", err=True)
                    sys.exit(1)
            else:
                click.echo(f"错误: 分支 '{branch_name}' 已存在", err=True)
                click.echo("使用 --force 强制删除并重新创建，或使用 -b 指定其他分支名称")
                sys.exit(1)

        # 8. 检查工作区状态
        if not no_checkout:
            is_clean, status_msg = check_working_directory_clean()

            if not is_clean:
                click.echo(f"警告: 工作区有未提交的修改: {status_msg}")
                click.echo()

                # 根据参数决定如何处理
                should_stash = stash
                if should_stash is None:
                    # 询问用户
                    choice = click.prompt(
                        "如何处理未提交的修改？\n"
                        "  1) 使用 stash 保存（推荐）\n"
                        "  2) 取消操作\n"
                        "  3) 强制继续（可能丢失修改）\n"
                        "请选择",
                        type=click.Choice(["1", "2", "3"]),
                        default="1",
                    )

                    if choice == "1":
                        should_stash = True
                    elif choice == "2":
                        click.echo("操作已取消")
                        sys.exit(0)
                    else:  # choice == "3"
                        should_stash = False

                # 执行 stash
                if should_stash:
                    click.echo("正在 stash 当前修改...")
                    success, msg = stash_changes(include_untracked=True)
                    if not success:
                        click.echo(f"错误: {msg}", err=True)
                        sys.exit(1)
                    click.echo(f"✓ {msg}")
                    click.echo("  使用 'git stash pop' 恢复修改")
                    click.echo()

        # 9. 拉取 change
        click.echo(f"正在从 Gerrit 拉取 change {change_number}...")
        success, msg = fetch_change_ref(str(change_number), ref_spec)
        if not success:
            click.echo(f"错误: {msg}", err=True)
            sys.exit(1)
        click.echo(f"✓ {msg}")

        # 10. 创建并切换分支
        if not no_checkout:
            click.echo(f"正在创建并切换到分支 '{branch_name}'...")

            # 先切换到 FETCH_HEAD
            success, msg = checkout_fetch_head()
            if not success:
                click.echo(f"错误: {msg}", err=True)
                sys.exit(1)

            # 创建新分支
            success, msg = checkout_branch(branch_name, create=True)
            if not success:
                click.echo(f"错误: {msg}", err=True)
                sys.exit(1)

            click.echo(f"✓ {msg}")
            click.echo()
            click.echo(f"成功! 已拉取 Change {change_number} 到分支 '{branch_name}'")
            click.echo(f"当前分支: {branch_name}")
        else:
            click.echo()
            click.echo(f"成功! 已拉取 Change {change_number}")
            click.echo("使用 'git checkout FETCH_HEAD' 切换到该 change")

        # 11. 提示后续操作
        click.echo()
        click.echo("后续操作:")
        click.echo(f"  - 查看代码: git log -1 --stat")
        click.echo(f"  - 查看 diff: git diff {change.branch}")
        if not no_checkout:
            current = get_current_branch()
            if current:
                click.echo(f"  - 返回原分支: git checkout {change.branch}")
            click.echo(f"  - 删除此分支: git checkout {change.branch} && git branch -D {branch_name}")

    except GerritCliError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
