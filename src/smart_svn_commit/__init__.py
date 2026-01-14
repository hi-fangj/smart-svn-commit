"""
Smart SVN Commit - AI 驱动的 SVN 提交助手

提供 PyQt5 GUI 界面，支持 AI 生成提交消息和 TortoiseSVN 集成。
"""

__version__ = "3.0.20"
__author__ = "Your Name"
__license__ = "MIT"

# 导出主要 API
from .ai.factory import generate_commit_message
from .core.commit import execute_svn_commit
from .core.config import init_config, load_config, save_config
from .core.fs_helper import FileSystemHelper
from .core.parser import parse_svn_status
from .core.svn_executor import SVNCommandExecutor

__all__ = [
    "__version__",
    "SVNCommandExecutor",
    "FileSystemHelper",
    "load_config",
    "save_config",
    "init_config",
    "parse_svn_status",
    "execute_svn_commit",
    "generate_commit_message",
]
