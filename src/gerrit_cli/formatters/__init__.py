"""Output Formatter Module"""

from gerrit_cli.formatters.base import Formatter
from gerrit_cli.formatters.json import JsonFormatter
from gerrit_cli.formatters.table import TableFormatter


def get_formatter(format_type: str) -> Formatter:
    """Get formatter instance

    Args:
        format_type: Format type (table or json)

    Returns:
        Formatter instance

    Raises:
        ValueError: Unsupported format type
    """
    if format_type == "table":
        return TableFormatter()
    elif format_type == "json":
        return JsonFormatter()
    else:
        raise ValueError(f"Unsupported format type: {format_type}")


__all__ = ["Formatter", "TableFormatter", "JsonFormatter", "get_formatter"]
