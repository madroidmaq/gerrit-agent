"""Review 命令"""

import sys

import click

from gerrit_cli.client.api import GerritClient
from gerrit_cli.client.models import ReviewInput
from gerrit_cli.utils.exceptions import GerritCliError


@click.command()
@click.argument("change_id")
@click.option("-m", "--message", help="Review 消息")
@click.option(
    "--code-review",
    type=click.Choice(["+2", "+1", "0", "-1", "-2"]),
    help="Code-Review 打分",
)
@click.option(
    "--verified",
    type=click.Choice(["+1", "0", "-1"]),
    help="Verified 打分",
)
@click.option("-f", "--file", "file_path", type=click.Path(exists=True), help="从文件读取消息")
@click.option("--submit", is_flag=True, help="Review 后直接提交")
@click.pass_context
def review(
    ctx: click.Context,
    change_id: str,
    message: str | None,
    code_review: str | None,
    verified: str | None,
    file_path: str | None,
    submit: bool,
) -> None:
    """发送 review（打分+评论）

    示例:
        gerrit review 12345 --code-review +2 -m "LGTM"
        gerrit review 12345 --code-review -1 -m "需要修改"
        gerrit review 12345 --code-review +2 --verified +1 --submit
        gerrit review 12345 -f review.txt --code-review +1
    """
    config = ctx.obj["config"]

    try:
        # 获取消息内容
        review_message = None
        if message:
            review_message = message
        elif file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                review_message = f.read()

        # 构建标签
        labels: dict[str, int] = {}
        if code_review:
            labels["Code-Review"] = int(code_review)
        if verified:
            labels["Verified"] = int(verified)

        # 验证：至少需要消息或标签
        if not review_message and not labels:
            click.echo("错误: 必须提供消息（-m 或 -f）或打分（--code-review 或 --verified）", err=True)
            sys.exit(1)

        # 构建 ReviewInput
        review_input = ReviewInput(message=review_message, labels=labels if labels else None)

        # 调用 API
        with GerritClient(config.url, config.username, config.password) as client:
            result = client.set_review(change_id, "current", review_input)

            # 输出结果
            click.echo(f"✓ Review 已发送到 Change {change_id}")

            if result.labels:
                label_text = ", ".join([f"{k}: {v:+d}" for k, v in result.labels.items()])
                click.echo(f"  标签: {label_text}")

            if review_message:
                click.echo(f"  消息: {review_message[:100]}{'...' if len(review_message) > 100 else ''}")

            # TODO: 实现 submit 功能
            if submit:
                click.echo("  注意: --submit 功能暂未实现", err=True)

    except GerritCliError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
