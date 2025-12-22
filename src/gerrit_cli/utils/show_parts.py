"""Display parts utility for gerrit show command"""

from typing import Optional

# Available parts and their abbreviations
AVAILABLE_PARTS = {
    "metadata": "m",
    "files": "f",
    "diff": "d",
    "messages": "msg",
    "comments": "c",
}

# Default parts to display (excluding diff for faster performance)
DEFAULT_PARTS = ["metadata", "files", "messages", "comments"]


def parse_parts_option(parts_str: str) -> list[str]:
    """Parse --parts option

    Supported formats:
    - "all" -> All parts
    - "m,f,d" -> Abbreviations
    - "metadata,files,diff" -> Full names
    - "m,files,d" -> Mixed

    Args:
        parts_str: Value of --parts option

    Returns:
        List of part names (full names)

    Raises:
        ValueError: If contains unknown part names

    Examples:
        >>> parse_parts_option("m,f,d")
        ['metadata', 'files', 'diff']

        >>> parse_parts_option("metadata,diff")
        ['metadata', 'diff']

        >>> parse_parts_option("all")
        ['metadata', 'files', 'diff', 'messages', 'comments']
    """
    # Special value: all
    if parts_str == "all":
        return list(AVAILABLE_PARTS.keys())

    # Parse comma-separated values
    parts = []
    abbr_to_full = {abbr: full for full, abbr in AVAILABLE_PARTS.items()}

    for item in parts_str.split(","):
        item = item.strip()

        if not item:
            continue

        # Check if it's a full name
        if item in AVAILABLE_PARTS:
            parts.append(item)
        # Check if it's an abbreviation
        elif item in abbr_to_full:
            parts.append(abbr_to_full[item])
        else:
            # Unknown part
            available = []
            for full, abbr in AVAILABLE_PARTS.items():
                available.append(f"{full}({abbr})")
            raise ValueError(
                f"Unknown part: '{item}'\n"
                f"Available parts: {', '.join(available)}"
            )

    return parts


def get_parts_to_show(parts_option: Optional[str] = None) -> dict[str, bool]:
    """Get parts to display

    Args:
        parts_option: Value of --parts option, None means use default

    Returns:
        Mapping from part names to whether they should be displayed
        Example: {"metadata": True, "files": True, "diff": False, ...}
    """
    if parts_option:
        parts_list = parse_parts_option(parts_option)
    else:
        parts_list = DEFAULT_PARTS

    # Convert to dictionary (all parts default to False, specified ones set to True)
    return {part: (part in parts_list) for part in AVAILABLE_PARTS.keys()}
