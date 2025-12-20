"""命令模块"""

from gerrit_cli.commands.change import change
from gerrit_cli.commands.review import review

__all__ = ["change", "review"]
