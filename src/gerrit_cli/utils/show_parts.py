"""gerrit show 命令的部分显示工具"""

from typing import Optional

# 可用部分及其缩写
AVAILABLE_PARTS = {
    "metadata": "m",
    "files": "f",
    "diff": "d",
    "messages": "msg",
    "comments": "c",
}

# 默认显示的部分（不含 diff，加快速度）
DEFAULT_PARTS = ["metadata", "files", "messages", "comments"]


def parse_parts_option(parts_str: str) -> list[str]:
    """解析 --parts 选项

    支持格式：
    - "all" -> 所有部分
    - "m,f,d" -> 缩写
    - "metadata,files,diff" -> 完整名称
    - "m,files,d" -> 混合

    Args:
        parts_str: --parts 选项的值

    Returns:
        部分名称列表（完整名称）

    Raises:
        ValueError: 如果包含未知的部分名称

    Examples:
        >>> parse_parts_option("m,f,d")
        ['metadata', 'files', 'diff']

        >>> parse_parts_option("metadata,diff")
        ['metadata', 'diff']

        >>> parse_parts_option("all")
        ['metadata', 'files', 'diff', 'messages', 'comments']
    """
    # 特殊值：all
    if parts_str == "all":
        return list(AVAILABLE_PARTS.keys())

    # 解析逗号分隔的值
    parts = []
    abbr_to_full = {abbr: full for full, abbr in AVAILABLE_PARTS.items()}

    for item in parts_str.split(","):
        item = item.strip()

        if not item:
            continue

        # 检查是否是完整名称
        if item in AVAILABLE_PARTS:
            parts.append(item)
        # 检查是否是缩写
        elif item in abbr_to_full:
            parts.append(abbr_to_full[item])
        else:
            # 未知的部分
            available = []
            for full, abbr in AVAILABLE_PARTS.items():
                available.append(f"{full}({abbr})")
            raise ValueError(
                f"Unknown part: '{item}'\n"
                f"Available parts: {', '.join(available)}"
            )

    return parts


def get_parts_to_show(parts_option: Optional[str] = None) -> dict[str, bool]:
    """获取要显示的部分

    Args:
        parts_option: --parts 选项的值，None 表示使用默认

    Returns:
        部分名称到是否显示的映射
        例如：{"metadata": True, "files": True, "diff": False, ...}
    """
    if parts_option:
        parts_list = parse_parts_option(parts_option)
    else:
        parts_list = DEFAULT_PARTS

    # 转换为字典（所有部分默认 False，指定的设为 True）
    return {part: (part in parts_list) for part in AVAILABLE_PARTS.keys()}
