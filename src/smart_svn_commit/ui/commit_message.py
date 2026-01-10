"""
提交消息生成模块（UI 专用）

此模块提供 UI 层的提交消息生成功能，实际上是对 AI 模块的封装。
"""

from typing import List

from ..ai.factory import generate_commit_message as ai_generate_message


def generate_commit_message(files: List[str]) -> str:
    """
    根据选中的文件生成 Conventional Commits 格式的提交消息。
    优先使用 AI API，如果 API 未配置或失败，则降级到关键词匹配。

    Args:
        files: 选中的文件路径列表

    Returns:
        生成的提交消息字符串
    """
    return ai_generate_message(files)

