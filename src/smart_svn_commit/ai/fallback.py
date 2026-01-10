"""
基于关键词的提交消息生成器（降级方案）
"""

from typing import Dict, List

# 默认提交消息
DEFAULT_MESSAGE = "chore: 提交变更"
DEFAULT_DESCRIPTION = "提交变更"

# 文件路径到类型的映射（基于常见模式）
PATH_TYPE_PATTERNS = {
    "fix": ["fix", "bug", "hotfix"],
    "feat": ["feature", "new", "add"],
    "docs": ["doc", "readme", "changelog"],
    "style": ["style", "format"],
    "refactor": ["refactor", "rewrite"],
    "perf": ["perf", "optimize", "performance"],
    "test": ["test", "spec"],
    "chore": ["chore", "build", "ci", "deps"],
    "build": ["build", "package", "release"],
}

# 文件路径到范围的映射
PATH_SCOPE_PATTERNS = {
    "guild": ["guild", "clan"],
    "battle": ["battle", "fight", "combat"],
    "chat": ["chat", "message", "mail"],
    "player": ["player", "hero", "character", "role"],
    "ui": ["ui", "view", "panel", "window", "dialog", "popup"],
    "network": ["network", "net", "protocol", "rpc"],
    "config": ["config", "setting", "option"],
    "art": ["art", "asset", "sprite", "texture", "model", "animation"],
    "audio": ["audio", "sound", "music", "voice"],
}


def generate_commit_message_by_keywords(files: List[str]) -> str:
    """
    基于文件路径关键词生成提交消息（降级方案）

    Args:
        files: 选中的文件路径列表

    Returns:
        生成的提交消息字符串
    """
    if not files:
        return DEFAULT_MESSAGE

    type_counts, scope_counts = _analyze_file_paths(files)

    commit_type = _get_most_common(type_counts, "chore")
    commit_scope = _get_most_common(scope_counts, "")

    return _format_commit_message(commit_type, commit_scope)


def _analyze_file_paths(files: List[str]) -> tuple[Dict[str, int], Dict[str, int]]:
    """
    分析文件路径，统计类型和范围出现次数

    Args:
        files: 文件路径列表

    Returns:
        (类型计数字典, 范围计数字典)
    """
    type_counts: Dict[str, int] = {}
    scope_counts: Dict[str, int] = {}

    for file_path in files:
        path_lower = file_path.lower()

        # 检测类型
        for type_name, patterns in PATH_TYPE_PATTERNS.items():
            if any(p in path_lower for p in patterns):
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # 检测范围
        for scope_name, patterns in PATH_SCOPE_PATTERNS.items():
            if any(p in path_lower for p in patterns):
                scope_counts[scope_name] = scope_counts.get(scope_name, 0) + 1

    return type_counts, scope_counts


def _get_most_common(counts: Dict[str, int], default: str) -> str:
    """
    从计数字典中获取出现最多的项

    Args:
        counts: 计数字典
        default: 默认值（如果字典为空）

    Returns:
        出现最多的键或默认值
    """
    if not counts:
        return default
    return max(counts, key=lambda k: counts[k])


def _format_commit_message(commit_type: str, commit_scope: str) -> str:
    """
    格式化提交消息

    Args:
        commit_type: 提交类型
        commit_scope: 提交范围

    Returns:
        格式化后的提交消息
    """
    if commit_scope:
        return f"{commit_type}({commit_scope}): {DEFAULT_DESCRIPTION}"
    return f"{commit_type}: {DEFAULT_DESCRIPTION}"
