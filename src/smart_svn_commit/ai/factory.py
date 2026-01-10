"""
提交消息生成工厂 - 协调 AI 和降级方案
"""

from typing import List

from .diff import get_multiple_files_diff
from .fallback import generate_commit_message_by_keywords
from .generator import DEFAULT_MESSAGE, generate_commit_message_with_ai


def generate_commit_message(files: List[str]) -> str:
    """
    根据选中的文件生成 Conventional Commits 格式的提交消息
    优先使用 AI API，如果 API 未配置或失败，则降级到关键词匹配

    Args:
        files: 选中的文件路径列表

    Returns:
        生成的提交消息字符串
    """
    if not files:
        return DEFAULT_MESSAGE

    files_with_diff = get_multiple_files_diff(files)

    # 尝试使用 AI API 生成
    api_message = generate_commit_message_with_ai(files_with_diff)
    if api_message != DEFAULT_MESSAGE:
        return api_message

    # 降级到关键词匹配
    return generate_commit_message_by_keywords(files)
