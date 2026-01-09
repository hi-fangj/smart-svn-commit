"""
AI 模块 - 提交消息生成
"""

from .diff import get_file_diff
from .generator import generate_commit_message_with_ai
from .fallback import generate_commit_message_by_keywords
from .factory import generate_commit_message

__all__ = [
    "get_file_diff",
    "generate_commit_message_with_ai",
    "generate_commit_message_by_keywords",
    "generate_commit_message",
]
