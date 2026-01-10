"""
获取文件差异内容
"""

import subprocess
from typing import List


def get_file_diff(file_path: str) -> str:
    """
    获取文件的 SVN diff 内容

    Args:
        file_path: 文件路径

    Returns:
        diff 内容字符串，如果获取失败则返回空字符串
    """
    try:
        result = subprocess.run(
            ["svn", "diff", file_path],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="ignore",
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, OSError):
        pass
    return ""


def get_multiple_files_diff(file_paths: List[str]) -> List[dict[str, str]]:
    """
    批量获取多个文件的 diff 内容

    Args:
        file_paths: 文件路径列表

    Returns:
        包含 path 和 diff 的字典列表
    """
    return [
        {"path": file_path, "diff": get_file_diff(file_path)}
        for file_path in file_paths
    ]
