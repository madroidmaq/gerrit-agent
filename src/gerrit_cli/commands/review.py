"""Review Command"""

import re
import sys

import click

from gerrit_cli.client.api import GerritClient
from gerrit_cli.client.models import CommentInput, CommentRange, ReviewInput
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
@click.option(
    "--inline-comment",
    nargs=2,
    type=(str, str),
    multiple=True,
    help="Inline comment: file#location message (location: line, start-end, LxxCxx-LxxCxx)",
)
@click.option("--submit", is_flag=True, help="Submit change after review")
@click.pass_context
def review(
    ctx: click.Context,
    change_id: str,
    message: str | None,
    code_review: str | None,
    verified: str | None,
    file_path: str | None,
    inline_comment: list[tuple[str, str]],
    submit: bool,
) -> None:
    """Send review (score + comment)

    Examples:
        gerrit review 12345 --code-review +2 -m "LGTM"
        gerrit review 12345 --code-review -1 -m "Needs improvement"
        gerrit review 12345 --code-review +2 --verified +1 --submit
        gerrit review 12345 --code-review +2 --verified +1 --submit
        gerrit review 12345 -f review.txt --code-review +1
        gerrit review 12345 --inline-comment src/main.py 10 "Fix typo"
        gerrit review 12345 --inline-comment src/main.py#10 "Fix typo"
        gerrit review 12345 --inline-comment src/main.py#10-20 "Refactor this block"
        gerrit review 12345 --inline-comment src/main.py#L12C13-L12C19 "Specific syntax error"
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

        # Validation: Must provide message, labels, or inline comments
        if not review_message and not labels and not inline_comment:
            click.echo(
                "Error: Must provide message (-m or -f), scores (--code-review or --verified), or inline comments (--inline-comment)",
                err=True,
            )
            sys.exit(1)

        # Build ReviewInput
        comments: dict[str, list[CommentInput]] = {}
        for location_spec, m in inline_comment:
            if "#" not in location_spec:
                click.echo(f"Error: Invalid inline comment format '{location_spec}'. Expected 'file#location'", err=True)
                sys.exit(1)

            f, l_raw = location_spec.rsplit("#", 1)

            if f not in comments:
                comments[f] = []

            # Parse line or range
            line: int
            comment_range: CommentRange | None = None

            # Check for character range: L12C13-L12C19 (case insensitive)
            char_range_match = re.match(r"^L(\d+)C(\d+)-L(\d+)C(\d+)$", l_raw, re.IGNORECASE)
            if char_range_match:
                start_line, start_char, end_line, end_char = map(int, char_range_match.groups())
                line = end_line
                comment_range = CommentRange(
                    start_line=start_line,
                    start_character=start_char,
                    end_line=end_line,
                    end_character=end_char,
                )
            elif "-" in l_raw:
                try:
                    start, end = map(int, l_raw.split("-"))
                    line = end
                    comment_range = CommentRange(
                        start_line=start,
                        start_character=0,
                        end_line=end,
                        end_character=10000,
                    )
                except ValueError:
                    click.echo(
                        f"Error: Invalid line format '{l_raw}', expected 'line', 'start-end', or 'LnCm-LnCm'",
                        err=True,
                    )
                    sys.exit(1)
            else:
                try:
                    line = int(l_raw)
                except ValueError:
                    click.echo(f"Error: Invalid line number '{l_raw}'", err=True)
                    sys.exit(1)

            comments[f].append(CommentInput(line=line, message=m, range=comment_range))

        review_input = ReviewInput(
            message=review_message,
            labels=labels if labels else None,
            comments=comments if comments else None,
        )

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
