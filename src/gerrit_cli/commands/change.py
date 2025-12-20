"""Change Command Group"""

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
    """Change related commands"""
    pass


@change.command()
@click.option("-q", "--query", default="status:open", help="Query conditions (default: status:open)")
@click.option("-n", "--limit", default=25, type=int, help="Limit number of results (default: 25)")
@click.option("-o", "--owner", help="Filter by owner (use 'me' for current user)")
@click.option("-p", "--project", help="Filter by project")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
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
    """List changes

    Examples:
        gerrit list
        gerrit list -q "status:merged"
        gerrit list --owner me
        gerrit list --project myproject --format json
    """
    config = ctx.obj["config"]

    try:
        # Build query conditions
        query_parts = [query]

        if owner:
            if owner == "me":
                query_parts.append(f"owner:{config.username}")
            else:
                query_parts.append(f"owner:{owner}")

        if project:
            query_parts.append(f"project:{project}")

        final_query = " ".join(query_parts)

        # Call API
        with GerritClient(config.url, config.username, config.password) as client:
            changes = client.list_changes(
                query=final_query, options=["CURRENT_REVISION", "LABELS"], limit=limit
            )

        # Format output
        formatter = get_formatter(output_format)
        output = formatter.format_changes(changes)
        click.echo(output)

    except GerritCliError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@change.command()
@click.argument("change_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.option("--comments", is_flag=True, help="Show comments")
@click.option("--messages", is_flag=True, help="Show message history (default)")
@click.option("--files", is_flag=True, help="Show file list")
@click.pass_context
def view(
    ctx: click.Context,
    change_id: str,
    output_format: str,
    comments: bool,
    messages: bool,
    files: bool,
) -> None:
    """View change details

    CHANGE_ID can be a numeric ID, Change-Id, or full path

    Examples:
        gerrit show 12345
        gerrit show I1234567890abcdef
        gerrit show 12345 --comments
        gerrit show 12345 --format json
    """
    config = ctx.obj["config"]

    try:
        # Call API to get details
        with GerritClient(config.url, config.username, config.password) as client:
            change = client.get_change_detail(change_id)

            # If comments are needed
            if comments:
                comments_data = client.get_change_comments(change_id)
                # TODO: add comments to output

        # Format output
        formatter = get_formatter(output_format)
        output = formatter.format_change_detail(change, show_comments=comments)
        click.echo(output)

    except GerritCliError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@change.command()
@click.argument("change_id")
@click.option("-m", "--message", help="Comment message")
@click.option("-f", "--file", "file_path", type=click.Path(exists=True), help="Read comment from file")
@click.option("--draft", is_flag=True, help="Save as draft")
@click.pass_context
def comment(
    ctx: click.Context,
    change_id: str,
    message: str | None,
    file_path: str | None,
    draft: bool,
) -> None:
    """Add comment to change

    Examples:
        gerrit change comment 12345 -m "LGTM"
        gerrit change comment 12345 -f comment.txt
    """
    config = ctx.obj["config"]

    try:
        # Get comment content
        if message:
            comment_text = message
        elif file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                comment_text = f.read()
        else:
            click.echo("Error: Must provide -m or -f option", err=True)
            sys.exit(1)

        # Call API
        with GerritClient(config.url, config.username, config.password) as client:
            if draft:
                # TODO: Implement draft comment
                click.echo("Draft feature not implemented yet", err=True)
                sys.exit(1)
            else:
                result = client.add_comment(change_id, comment_text)
                click.echo(f"✓ Comment added to Change {change_id}", err=False)

    except GerritCliError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@change.command()
@click.argument("change_id")
@click.option("-b", "--branch", help="Local branch name (default: review/change-{change_id})")
@click.option("--force", is_flag=True, help="Force delete and recreate branch if exists")
@click.option("--no-checkout", is_flag=True, help="Only fetch, do not checkout")
@click.option(
    "--stash/--no-stash",
    default=None,
    help="Auto stash uncommitted changes (will prompt by default)",
)
@click.pass_context
def checkout(
    ctx: click.Context,
    change_id: str,
    branch: str | None,
    force: bool,
    no_checkout: bool,
    stash: bool | None,
) -> None:
    """Checkout change to local branch

    This command fetches a specified change from Gerrit to local, and creates a new branch.
    If the working directory has uncommitted changes, it will prompt you how to handle them.

    CHANGE_ID can be a numeric ID, Change-Id, or full path

    Examples:
        # Checkout change 12345 to new branch
        gerrit checkout 12345

        # Specify branch name
        gerrit checkout 12345 -b my-review-branch

        # Force recreate branch if exists
        gerrit checkout 12345 --force

        # Only fetch without checkout
        gerrit checkout 12345 --no-checkout

        # Auto stash uncommitted changes
        gerrit checkout 12345 --stash
    """
    config = ctx.obj["config"]

    try:
        # 1. Check if inside a Git repository
        if not check_git_repository():
            click.echo("Error: Current directory is not a Git repository", err=True)
            click.echo()
            click.echo("Please cd into the Gerrit project's Git repository before running this command.", err=True)
            click.echo()
            click.echo("Example:")
            click.echo("  cd /path/to/your/gerrit/project")
            click.echo("  gerrit checkout 12345")
            sys.exit(1)

        # 2. Get change info from Gerrit
        click.echo(f"Fetching info for Change {change_id}...")
        with GerritClient(config.url, config.username, config.password) as client:
            change = client.get_change(change_id, options=["CURRENT_REVISION", "DOWNLOAD_COMMANDS"])

        # 3. Verify current repo matches project
        repo_root = get_repo_root()
        if repo_root:
            click.echo(f"Current repo: {repo_root}")

        # Check if remote exists
        if not check_remote_exists("origin"):
            click.echo()
            click.echo("Warning: 'origin' remote not found in current Git repository", err=True)
            click.echo("Fetch operation may fail.", err=True)
            click.echo()

            if not click.confirm("Continue?", default=False):
                click.echo("Operation cancelled")
                sys.exit(0)
        else:
            # Get remote URL and warn user
            remote_url = get_git_remote_url("origin")
            if remote_url:
                click.echo(f"Remote URL: {remote_url}")

                # Simple check: if remote URL contains project name
                # Note: This is an heuristic check, not 100% reliable
                if change.project not in remote_url:
                    click.echo()
                    click.echo(f"⚠️  Warning: Current repo remote URL does not seem to match Change project", err=True)
                    click.echo(f"   Change Project: {change.project}", err=True)
                    click.echo(f"   Remote URL: {remote_url}", err=True)
                    click.echo()
                    click.echo("Possible reasons:")
                    click.echo("  1. You are running this command in the wrong Git repository")
                    click.echo(f"  2. You need to cd into '{change.project}' project directory")
                    click.echo()

                    if not click.confirm("Still want to continue fetch?", default=False):
                        click.echo("Operation cancelled")
                        click.echo()
                        click.echo("Suggestion:")
                        click.echo(f"  1. Find the Git repo directory for {change.project}")
                        click.echo("  2. cd into that directory")
                        click.echo(f"  3. Run again: gerrit checkout {change_id}")
                        sys.exit(0)

        # 4. Verify change info
        if not change.current_revision:
            click.echo("Error: Cannot get current revision for change", err=True)
            sys.exit(1)

        click.echo()

        # 5. Get ref spec
        # Gerrit ref format: refs/changes/[last 2 digits]/[change number]/[patch set number]
        change_number = change.number
        last_two = change_number % 100
        ref_spec = f"refs/changes/{last_two:02d}/{change_number}/1"

        click.echo(f"Change: {change.subject}")
        click.echo(f"Project: {change.project}")
        click.echo(f"Branch: {change.branch}")
        click.echo(f"Owner: {change.owner.name if change.owner else 'Unknown'}")
        click.echo(f"Ref: {ref_spec}")
        click.echo()

        # 6. Determine branch name
        if branch is None:
            branch_name = f"review/change-{change_number}"
        else:
            branch_name = branch

        # 7. Check if branch exists
        if branch_exists(branch_name):
            if force:
                click.echo(f"Warning: Branch '{branch_name}' exists, deleting...")
                current = get_current_branch()
                if current == branch_name:
                    click.echo("Error: Cannot delete current branch, please switch to another branch first", err=True)
                    sys.exit(1)
                success, msg = delete_branch(branch_name, force=True)
                if not success:
                    click.echo(f"Error: {msg}", err=True)
                    sys.exit(1)
            else:
                click.echo(f"Error: Branch '{branch_name}' already exists", err=True)
                click.echo("Use --force to force delete and recreate, or use -b to specify another branch name")
                sys.exit(1)

        # 8. Check working directory status
        if not no_checkout:
            is_clean, status_msg = check_working_directory_clean()

            if not is_clean:
                click.echo(f"Warning: Uncommitted changes in working directory: {status_msg}")
                click.echo()

                # Decide how to handle based on args
                should_stash = stash
                if should_stash is None:
                    # Ask user
                    choice = click.prompt(
                        "How to handle uncommitted changes?\n"
                        "  1) Stash changes (Recommended)\n"
                        "  2) Cancel operation\n"
                        "  3) Force continue (Changes may be lost)\n"
                        "Please choose",
                        type=click.Choice(["1", "2", "3"]),
                        default="1",
                    )

                    if choice == "1":
                        should_stash = True
                    elif choice == "2":
                        click.echo("Operation cancelled")
                        sys.exit(0)
                    else:  # choice == "3"
                        should_stash = False

                # Perform stash
                if should_stash:
                    click.echo("Stashing current changes...")
                    success, msg = stash_changes(include_untracked=True)
                    if not success:
                        click.echo(f"Error: {msg}", err=True)
                        sys.exit(1)
                    click.echo(f"✓ {msg}")
                    click.echo("  Use 'git stash pop' to restore changes")
                    click.echo()

        # 9. Fetch change
        click.echo(f"Fetching change {change_number} from Gerrit...")
        success, msg = fetch_change_ref(str(change_number), ref_spec)
        if not success:
            click.echo(f"Error: {msg}", err=True)
            sys.exit(1)
        click.echo(f"✓ {msg}")

        # 10. Create and checkout branch
        if not no_checkout:
            click.echo(f"Creating and switching to branch '{branch_name}'...")

            # Checkout FETCH_HEAD first
            success, msg = checkout_fetch_head()
            if not success:
                click.echo(f"Error: {msg}", err=True)
                sys.exit(1)

            # Create new branch
            success, msg = checkout_branch(branch_name, create=True)
            if not success:
                click.echo(f"Error: {msg}", err=True)
                sys.exit(1)

            click.echo(f"✓ {msg}")
            click.echo()
            click.echo(f"Success! Fetched Change {change_number} to branch '{branch_name}'")
            click.echo(f"Current branch: {branch_name}")
        else:
            click.echo()
            click.echo(f"Success! Fetched Change {change_number}")
            click.echo("Use 'git checkout FETCH_HEAD' to check it out")

        # 11. Next steps
        click.echo()
        click.echo("Next steps:")
        click.echo(f"  - View code: git log -1 --stat")
        click.echo(f"  - View diff: git diff {change.branch}")
        if not no_checkout:
            current = get_current_branch()
            if current:
                click.echo(f"  - Return to original branch: git checkout {change.branch}")
            click.echo(f"  - Delete this branch: git checkout {change.branch} && git branch -D {branch_name}")

    except GerritCliError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
