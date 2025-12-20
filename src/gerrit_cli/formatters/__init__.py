"""输出格式化器模块"""

from gerrit_cli.formatters.base import Formatter
from gerrit_cli.formatters.json import JsonFormatter
from gerrit_cli.formatters.table import TableFormatter


def get_formatter(format_type: str) -> Formatter:
    """获取格式化器实例

    Args:
        format_type: 格式类型（table 或 json）

    Returns:
        Formatter 实例

    Raises:
        ValueError: 不支持的格式类型
    """
    if format_type == "table":
        return TableFormatter()
    elif format_type == "json":
        return JsonFormatter()
    else:
        raise ValueError(f"不支持的格式类型: {format_type}")


__all__ = ["Formatter", "TableFormatter", "JsonFormatter", "get_formatter"]
