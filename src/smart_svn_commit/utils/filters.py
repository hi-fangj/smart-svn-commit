"""
文件过滤工具
"""

import re
from pathlib import Path
from typing import List, Tuple


def apply_ignore_patterns(
    files: List[Tuple[str, str]], ignore_patterns: List[str]
) -> List[Tuple[str, str]]:
    """
    应用忽略模式过滤文件列表

    Args:
        files: (状态, 文件路径) 元组列表
        ignore_patterns: 忽略模式列表

    Returns:
        过滤后的文件列表
    """
    if not ignore_patterns:
        return files

    filtered = []
    for status, file_path in files:
        should_ignore = _should_ignore_file(file_path, ignore_patterns)
        if not should_ignore:
            filtered.append((status, file_path))

    return filtered


def _should_ignore_file(file_path: str, ignore_patterns: List[str]) -> bool:
    """
    判断文件是否应该被忽略

    Args:
        file_path: 文件路径
        ignore_patterns: 忽略模式列表

    Returns:
        True 如果应该忽略，否则 False
    """
    for pattern in ignore_patterns:
        if pattern.endswith("/"):
            # 目录模式
            if file_path.startswith(pattern):
                return True
        elif pattern.startswith("*."):
            # 扩展名模式
            if file_path.endswith(pattern[1:]):
                return True
        elif "*" in pattern or "?" in pattern:
            # 通配符模式
            try:
                if Path(file_path).match(pattern):
                    return True
            except (ValueError, RuntimeError):
                pass
        else:
            # 完整路径或部分匹配
            if pattern in file_path:
                return True

    return False


def wildcard_filter(pattern: str, items: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    使用通配符过滤文件列表

    支持的通配符模式：
    - *.cs : 匹配所有 .cs 文件
    - Test*.cs : 匹配以 Test 开头且以 .cs 结尾的文件
    - *Test : 匹配以 Test 结尾的文件
    - *.cs* : 匹配包含 .cs 的文件

    Args:
        pattern: 通配符模式
        items: 原始项目列表

    Returns:
        过滤后的项目列表
    """
    # 将通配符模式转换为正则表达式
    regex_pattern = re.escape(pattern)
    regex_pattern = regex_pattern.replace(r"\*", ".*")
    regex_pattern = regex_pattern.replace(r"\?", ".")
    regex_pattern = f"^{regex_pattern}$"

    try:
        regex = re.compile(regex_pattern, re.IGNORECASE)
        return [(status, path) for status, path in items if regex.search(path)]
    except re.error:
        # 正则表达式无效，返回空列表
        return []


def text_filter(search_text: str, items: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    使用普通文本过滤（大小写不敏感）

    Args:
        search_text: 搜索文本
        items: 原始项目列表

    Returns:
        过滤后的项目列表
    """
    search_lower = search_text.lower()
    return [(status, path) for status, path in items if search_lower in path.lower()]
