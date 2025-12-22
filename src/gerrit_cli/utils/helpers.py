"""Helper Functions"""

import subprocess
from typing import Optional, Tuple, Union


class GitOperationError(Exception):
    """Git Operation Error"""

    pass


def run_git_command(command: list[str], cwd: Optional[str] = None) -> Tuple[bool, str]:
    """Run Git Command

    Args:
        command: List of Git command arguments (e.g. ['git', 'status'])
        cwd: Working directory (optional)

    Returns:
        Tuple of (Success, Output)
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def check_git_repository(path: str = ".") -> bool:
    """Check if current directory is a Git repository

    Args:
        path: Path to check

    Returns:
        True if it is a Git repository
    """
    success, _ = run_git_command(["git", "rev-parse", "--git-dir"], cwd=path)
    return success


def get_current_branch() -> Optional[str]:
    """Get current Git branch name

    Returns:
        Branch name, or None if not on a branch
    """
    success, output = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if success and output != "HEAD":
        return output
    return None


def check_working_directory_clean() -> Tuple[bool, str]:
    """Check if working directory is clean (no uncommitted changes)

    Returns:
        Tuple of (Is Clean, Status Description)
    """
    success, output = run_git_command(["git", "status", "--porcelain"])
    if not success:
        return False, "Failed to check Git status"

    if not output:
        return True, "Working directory clean"

    # Count changes
    lines = output.strip().split("\n")
    staged = sum(1 for line in lines if line[0] in "MADRC")
    unstaged = sum(1 for line in lines if line[1] in "MD")
    untracked = sum(1 for line in lines if line.startswith("??"))

    status_parts = []
    if staged > 0:
        status_parts.append(f"{staged} staged changes")
    if unstaged > 0:
        status_parts.append(f"{unstaged} unstaged changes")
    if untracked > 0:
        status_parts.append(f"{untracked} untracked files")

    return False, ", ".join(status_parts)


def stash_changes(include_untracked: bool = True) -> Tuple[bool, str]:
    """Stash current changes

    Args:
        include_untracked: Whether to include untracked files

    Returns:
        Tuple of (Success, Message)
    """
    command = ["git", "stash", "push", "-m", "gerrit-cli: auto stash before fetch"]
    if include_untracked:
        command.append("--include-untracked")

    success, output = run_git_command(command)
    if success:
        return True, "Stashed current changes"
    return False, f"Stash failed: {output}"


def pop_stash() -> Tuple[bool, str]:
    """Pop latest stash

    Returns:
        Tuple of (Success, Message)
    """
    success, output = run_git_command(["git", "stash", "pop"])
    if success:
        return True, "Restored previous changes"
    return False, f"Stash pop failed: {output}"


def fetch_change_ref(change_number: str, ref_spec: str) -> Tuple[bool, str]:
    """Fetch change ref from Gerrit

    Args:
        change_number: Change number
        ref_spec: Ref spec (e.g. refs/changes/45/12345/1)

    Returns:
        Tuple of (Success, Message)
    """
    success, output = run_git_command(["git", "fetch", "origin", ref_spec])
    if success:
        return True, f"Fetched change {change_number}"
    return False, f"Fetch failed: {output}"


def checkout_branch(branch_name: str, create: bool = True) -> Tuple[bool, str]:
    """Checkout branch

    Args:
        branch_name: Branch name
        create: Whether to create new branch

    Returns:
        Tuple of (Success, Message)
    """
    if create:
        command = ["git", "checkout", "-b", branch_name]
    else:
        command = ["git", "checkout", branch_name]

    success, output = run_git_command(command)
    if success:
        return True, f"Switched to branch {branch_name}"
    return False, f"Failed to checkout branch: {output}"


def checkout_fetch_head() -> Tuple[bool, str]:
    """Checkout FETCH_HEAD

    Returns:
        Tuple of (Success, Message)
    """
    success, output = run_git_command(["git", "checkout", "FETCH_HEAD"])
    if success:
        return True, "Switched to FETCH_HEAD"
    return False, f"Checkout failed: {output}"


def branch_exists(branch_name: str) -> bool:
    """Check if branch exists

    Args:
        branch_name: Branch name

    Returns:
        True if branch exists
    """
    success, _ = run_git_command(["git", "rev-parse", "--verify", branch_name])
    return success


def delete_branch(branch_name: str, force: bool = False) -> Tuple[bool, str]:
    """Delete branch

    Args:
        branch_name: Branch name
        force: Whether to force delete

    Returns:
        Tuple of (Success, Message)
    """
    flag = "-D" if force else "-d"
    success, output = run_git_command(["git", "branch", flag, branch_name])
    if success:
        return True, f"Deleted branch {branch_name}"
    return False, f"Failed to delete branch: {output}"


def get_git_remote_url(remote_name: str = "origin") -> Optional[str]:
    """Get Git remote URL

    Args:
        remote_name: Remote name (default: origin)

    Returns:
        Remote URL, or None if not found
    """
    success, output = run_git_command(["git", "remote", "get-url", remote_name])
    if success:
        return output.strip()
    return None


def get_repo_root() -> Optional[str]:
    """Get Git repository root directory

    Returns:
        Absolute path to repo root, or None if not in a repo
    """
    success, output = run_git_command(["git", "rev-parse", "--show-toplevel"])
    if success:
        return output.strip()
    return None


def check_remote_exists(remote_name: str = "origin") -> bool:
    """Check if specified remote exists

    Args:
        remote_name: Remote name

    Returns:
        True if remote exists
    """
    success, output = run_git_command(["git", "remote"])
    if success:
        remotes = output.strip().split("\n")
        return remote_name in remotes
    return False


def shorten_path(path: str, max_length: int = 60) -> str:
    """Shorten a file path by truncating or compressing.

    Tiered Strategies:
    1. Middle Truncation: 'first/part/.../filename.kt'
    2. Directory Compression: 'f/p/intermediate/filename.kt'
    3. Filename Only: '.../filename.kt'
    4. Filename Truncation: '...name.kt'
    """
    if len(path) <= max_length:
        return path

    if max_length < 5:
        return f"...{path[-(max_length-3):]}" if max_length > 3 else "..."

    parts = path.split("/")
    first = parts[0]
    last = parts[-1]

    # Tier 1: Middle Truncation "first/.../last" (at least 3 parts)
    if len(parts) >= 3:
        fixed_parts_len = len(first) + 5 + len(last)  # 5 for "/.../"
        if fixed_parts_len <= max_length:
            remaining = max_length - fixed_parts_len
            middle_parts = []
            curr_len = 0
            for p in reversed(parts[1:-1]):
                if curr_len + len(p) + 1 <= remaining:
                    middle_parts.insert(0, p)
                    curr_len += len(p) + 1
                else:
                    break
            if middle_parts:
                return f"{first}/.../{'/'.join(middle_parts)}/{last}"
            else:
                return f"{first}/.../{last}"

    # Tier 2: Directory Compression "f/p/intermediate/last"
    if len(parts) >= 2:
        # Keep last part, compress others to 1 char + /
        compressed_parts = [p[0] for p in parts[:-1]]
        compressed_prefix = "/".join(compressed_parts) + "/"
        if len(compressed_prefix) + len(last) <= max_length:
            return f"{compressed_prefix}{last}"

    # Tier 3: Filename Only ".../last"
    if len(last) + 4 <= max_length:
        return f".../{last}"

    # Tier 4: Filename Truncation "...last"
    return f"...{last[-(max_length-3):]}"
