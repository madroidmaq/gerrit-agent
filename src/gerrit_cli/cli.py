"""CLI Main Entry Point"""

import sys

import click

from gerrit_cli import __version__
from gerrit_cli.config import GerritConfig
from gerrit_cli.utils.exceptions import GerritCliError


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Gerrit CLI - Gerrit Code Review Command Line Tool

    Please configure environment variables before use:
    - GERRIT_URL: Gerrit Server URL
    - GERRIT_USERNAME: Username
    - GERRIT_PASSWORD or GERRIT_TOKEN: Password or HTTP Token
    """
    # Ensure ctx.obj exists
    ctx.ensure_object(dict)

    # If viewing help, skip config loading
    if "--help" in sys.argv or len(sys.argv) == 1:
        return

    try:
        # Load config and store in context
        ctx.obj["config"] = GerritConfig.from_env()
    except GerritCliError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Register command groups
from gerrit_cli.commands.change import change
from gerrit_cli.commands.review import review

main.add_command(change)
main.add_command(review)

# Root-level Alias (Scheme B)
main.add_command(change.commands["list"], name="list")
main.add_command(change.commands["view"], name="show")
main.add_command(change.commands["checkout"], name="checkout")

# Group Alias (Scheme A)
main.add_command(change, name="c")


if __name__ == "__main__":
    main()
