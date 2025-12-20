"""CLI 主入口"""

import sys

import click

from gerrit_cli import __version__
from gerrit_cli.config import GerritConfig
from gerrit_cli.utils.exceptions import GerritCliError


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Gerrit CLI - Gerrit Code Review 命令行工具

    使用前请配置环境变量：
    - GERRIT_URL: Gerrit 服务器 URL
    - GERRIT_USERNAME: 用户名
    - GERRIT_PASSWORD 或 GERRIT_TOKEN: 密码或 HTTP Token
    """
    # 确保 ctx.obj 存在
    ctx.ensure_object(dict)

    # 如果是查看帮助信息，不需要加载配置
    if "--help" in sys.argv or len(sys.argv) == 1:
        return

    try:
        # 加载配置并存储在 context 中
        ctx.obj["config"] = GerritConfig.from_env()
    except GerritCliError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


# 注册命令组
from gerrit_cli.commands.change import change
from gerrit_cli.commands.review import review

main.add_command(change)
main.add_command(review)


if __name__ == "__main__":
    main()
