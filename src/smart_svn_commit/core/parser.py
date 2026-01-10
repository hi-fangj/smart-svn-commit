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
        # 只去除行尾空白，保留行首空格（用于识别属性状态）
        line = line.rstrip()
        if (
            not line
            or line.startswith(("svn: warning:", "svn: E"))
            or "ng status" in line
        ):
            continue

        # SVN status 格式: "M       Assets/Scripts/File.cs"
        # 第 1 列：内容状态，第 2 列：属性状态
        if len(line) > 8:
            # 第一列：内容状态
            content_status = line[0] if line[0] != " " else None
            # 第二列：属性状态
            prop_status = line[1] if len(line) > 1 and line[1] in "MC" else None

            # 优先使用内容状态，如果没有则使用属性状态
            status_code = content_status or prop_status

            # 如果是纯属性变动，使用 _ 前缀区分
            if prop_status and not content_status:
                status_code = f"_{prop_status}"

            file_path = line[8:].strip()
            if status_code and file_path:
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

