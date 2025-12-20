"""辅助函数"""

import subprocess


class GitOperationError(Exception):
    """Git 操作错误"""

    pass


def run_git_command(command: list[str], cwd: str | None = None) -> tuple[bool, str]:
    """运行 Git 命令

    Args:
        command: Git 命令列表（如 ['git', 'status']）
        cwd: 工作目录（可选）

    Returns:
        (成功, 输出内容) 元组
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
    """检查当前目录是否是 Git 仓库

    Args:
        path: 要检查的路径

    Returns:
        是否是 Git 仓库
    """
    success, _ = run_git_command(["git", "rev-parse", "--git-dir"], cwd=path)
    return success


def get_current_branch() -> str | None:
    """获取当前 Git 分支名称

    Returns:
        分支名称，如果不在分支上则返回 None
    """
    success, output = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if success and output != "HEAD":
        return output
    return None


def check_working_directory_clean() -> tuple[bool, str]:
    """检查工作区是否干净（没有未提交的修改）

    Returns:
        (是否干净, 状态描述) 元组
    """
    success, output = run_git_command(["git", "status", "--porcelain"])
    if not success:
        return False, "无法检查 Git 状态"

    if not output:
        return True, "工作区干净"

    # 统计修改
    lines = output.strip().split("\n")
    staged = sum(1 for line in lines if line[0] in "MADRC")
    unstaged = sum(1 for line in lines if line[1] in "MD")
    untracked = sum(1 for line in lines if line.startswith("??"))

    status_parts = []
    if staged > 0:
        status_parts.append(f"{staged} 个已暂存的修改")
    if unstaged > 0:
        status_parts.append(f"{unstaged} 个未暂存的修改")
    if untracked > 0:
        status_parts.append(f"{untracked} 个未跟踪的文件")

    return False, "、".join(status_parts)


def stash_changes(include_untracked: bool = True) -> tuple[bool, str]:
    """暂存当前修改

    Args:
        include_untracked: 是否包含未跟踪的文件

    Returns:
        (是否成功, 消息) 元组
    """
    command = ["git", "stash", "push", "-m", "gerrit-cli: auto stash before fetch"]
    if include_untracked:
        command.append("--include-untracked")

    success, output = run_git_command(command)
    if success:
        return True, "已使用 stash 保存当前修改"
    return False, f"Stash 失败: {output}"


def pop_stash() -> tuple[bool, str]:
    """恢复最近的 stash

    Returns:
        (是否成功, 消息) 元组
    """
    success, output = run_git_command(["git", "stash", "pop"])
    if success:
        return True, "已恢复之前的修改"
    return False, f"恢复 stash 失败: {output}"


def fetch_change_ref(change_number: str, ref_spec: str) -> tuple[bool, str]:
    """从 Gerrit 拉取 change 的 ref

    Args:
        change_number: Change 编号
        ref_spec: Ref spec（如 refs/changes/45/12345/1）

    Returns:
        (是否成功, 消息) 元组
    """
    success, output = run_git_command(["git", "fetch", "origin", ref_spec])
    if success:
        return True, f"已拉取 change {change_number}"
    return False, f"拉取失败: {output}"


def checkout_branch(branch_name: str, create: bool = True) -> tuple[bool, str]:
    """切换到指定分支

    Args:
        branch_name: 分支名称
        create: 是否创建新分支

    Returns:
        (是否成功, 消息) 元组
    """
    if create:
        command = ["git", "checkout", "-b", branch_name]
    else:
        command = ["git", "checkout", branch_name]

    success, output = run_git_command(command)
    if success:
        return True, f"已切换到分支 {branch_name}"
    return False, f"切换分支失败: {output}"


def checkout_fetch_head() -> tuple[bool, str]:
    """切换到 FETCH_HEAD

    Returns:
        (是否成功, 消息) 元组
    """
    success, output = run_git_command(["git", "checkout", "FETCH_HEAD"])
    if success:
        return True, "已切换到 FETCH_HEAD"
    return False, f"切换失败: {output}"


def branch_exists(branch_name: str) -> bool:
    """检查分支是否存在

    Args:
        branch_name: 分支名称

    Returns:
        分支是否存在
    """
    success, _ = run_git_command(["git", "rev-parse", "--verify", branch_name])
    return success


def delete_branch(branch_name: str, force: bool = False) -> tuple[bool, str]:
    """删除分支

    Args:
        branch_name: 分支名称
        force: 是否强制删除

    Returns:
        (是否成功, 消息) 元组
    """
    flag = "-D" if force else "-d"
    success, output = run_git_command(["git", "branch", flag, branch_name])
    if success:
        return True, f"已删除分支 {branch_name}"
    return False, f"删除分支失败: {output}"


def get_git_remote_url(remote_name: str = "origin") -> str | None:
    """获取 Git remote 的 URL

    Args:
        remote_name: Remote 名称（默认: origin）

    Returns:
        Remote URL，如果不存在则返回 None
    """
    success, output = run_git_command(["git", "remote", "get-url", remote_name])
    if success:
        return output.strip()
    return None


def get_repo_root() -> str | None:
    """获取 Git 仓库的根目录

    Returns:
        仓库根目录的绝对路径，如果不在仓库中则返回 None
    """
    success, output = run_git_command(["git", "rev-parse", "--show-toplevel"])
    if success:
        return output.strip()
    return None


def check_remote_exists(remote_name: str = "origin") -> bool:
    """检查指定的 remote 是否存在

    Args:
        remote_name: Remote 名称

    Returns:
        Remote 是否存在
    """
    success, output = run_git_command(["git", "remote"])
    if success:
        remotes = output.strip().split("\n")
        return remote_name in remotes
    return False
