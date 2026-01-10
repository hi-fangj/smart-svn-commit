"""
Windows 模块辅助函数 - 提供共享的 SVN 工具函数
"""

from pathlib import Path


def is_svn_working_copy(path: str) -> bool:
    """
    检查目录是否是 SVN 工作副本

    Args:
        path: 目录路径

    Returns:
        是否是 SVN 工作副本
    """
    try:
        return (Path(path) / ".svn").is_dir()
    except Exception:
        return False


def get_install_dir() -> Path:
    """
    获取安装目录

    Returns:
        安装目录路径
    """
    return Path(__file__).parent.parent.parent.parent
