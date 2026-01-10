"""
基于关键词的提交消息生成器（降级方案）
"""

from typing import Dict, List


def generate_commit_message_by_keywords(files: List[str]) -> str:
    """
    基于文件路径关键词生成提交消息（降级方案）

    Args:
        files: 选中的文件路径列表

    Returns:
        生成的提交消息字符串
    """
    if not files:
        return "chore: 提交变更"

    # 文件路径到类型的映射（基于常见模式）
    path_type_patterns = {
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
    path_scope_patterns = {
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

    # 分析文件路径，统计类型和范围
    type_counts: Dict[str, int] = {}
    scope_counts: Dict[str, int] = {}

    for file_path in files:
        path_lower = file_path.lower()

        # 检测类型
        for type_name, patterns in path_type_patterns.items():
            if any(p in path_lower for p in patterns):
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # 检测范围
        for scope_name, patterns in path_scope_patterns.items():
            if any(p in path_lower for p in patterns):
                scope_counts[scope_name] = scope_counts.get(scope_name, 0) + 1

    # 选择最常见的类型和范围
    commit_type = (
        max(type_counts, key=lambda k: type_counts[k]) if type_counts else "chore"
    )
    commit_scope = (
        max(scope_counts, key=lambda k: scope_counts[k]) if scope_counts else ""
    )

    # 构建提交消息
    if commit_scope:
        return f"{commit_type}({commit_scope}): 提交变更"
    else:
        return f"{commit_type}: 提交变更"
