"""Review Command"""

import sys

import click

from gerrit_cli.client.api import GerritClient
from gerrit_cli.client.models import ReviewInput
from gerrit_cli.utils.exceptions import GerritCliError


@click.command()
@click.argument("change_id")
@click.option("-m", "--message", help="Review message")
@click.option(
    "--code-review",
    type=click.Choice(["+2", "+1", "0", "-1", "-2"]),
    help="Code-Review score",
)
@click.option(
    "--verified",
    type=click.Choice(["+1", "0", "-1"]),
    help="Verified score",
)
@click.option("-f", "--file", "file_path", type=click.Path(exists=True), help="Read message from file")
@click.option("--submit", is_flag=True, help="Submit change after review")
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
    """Send review (score + comment)

    Examples:
        gerrit review 12345 --code-review +2 -m "LGTM"
        gerrit review 12345 --code-review -1 -m "Needs improvement"
        gerrit review 12345 --code-review +2 --verified +1 --submit
        gerrit review 12345 -f review.txt --code-review +1
    """
    config = ctx.obj["config"]

    try:
        # Get message content
        review_message = None
        if message:
            review_message = message
        elif file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                review_message = f.read()

        # Build labels
        labels: dict[str, int] = {}
        if code_review:
            labels["Code-Review"] = int(code_review)
        if verified:
            labels["Verified"] = int(verified)

        # Validation: Must provide message or labels
        if not review_message and not labels:
            click.echo("Error: Must provide message (-m or -f) or scores (--code-review or --verified)", err=True)
            sys.exit(1)

        # Build ReviewInput
        review_input = ReviewInput(message=review_message, labels=labels if labels else None)

        # Call API
        with GerritClient(config.url, config.username, config.password) as client:
            result = client.set_review(change_id, "current", review_input)

            # Output result
            click.echo(f"✓ Review sent to Change {change_id}")

            if result.labels:
                label_text = ", ".join([f"{k}: {v:+d}" for k, v in result.labels.items()])
                click.echo(f"  Labels: {label_text}")

            if review_message:
                click.echo(f"  Message: {review_message[:100]}{'...' if len(review_message) > 100 else ''}")

            # TODO: Implement submit feature
            if submit:
                click.echo(f"  Note: --submit feature not implemented yet", err=True)

    except GerritCliError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
