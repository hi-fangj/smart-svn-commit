"""
SVN 状态解析器
"""

from typing import List, Optional, Tuple

# SVN 状态码常量
SVN_STATUS_CODES = {"M", "A", "D", "?", "!", "C", "R", "~", "S"}

# 显示文本分隔符（用于 UI 显示）
STATUS_PREFIX_SEPARATOR = "] "


def parse_svn_status(status_output: str) -> List[Tuple[str, str]]:
    """
    解析 SVN 状态输出，提取文件路径和状态

    Args:
        status_output: svn status 命令的原始输出

    Returns:
        (状态, 文件路径) 元组列表
    """
    files = []
    for line in status_output.splitlines():
        line = line.strip()
        if (
            not line
            or line.startswith(("svn: warning:", "svn: E"))
            or "ng status" in line
        ):
            continue

        # SVN status 格式: "M       Assets/Scripts/File.cs"
        # 前 8 个字符是工作区状态（第 1 个字符）和版本库状态（第 8 个字符）
        if len(line) > 8 and line[0] != " ":
            status_code, file_path = line[0], line[8:].strip()
            if status_code in SVN_STATUS_CODES and file_path:
                files.append((status_code, file_path))

    return files


def extract_path_from_display_text(
    display_text: str, separator: str = STATUS_PREFIX_SEPARATOR
) -> Optional[str]:
    """
    从显示文本中提取文件路径

    Args:
        display_text: 显示文本，格式为 "[M] path" 或类似
        separator: 状态和路径的分隔符

    Returns:
        提取的文件路径，如果格式不匹配则返回 None
    """
    if separator in display_text:
        return display_text.split(separator, 1)[1]
    return None

