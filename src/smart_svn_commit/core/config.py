"""
配置管理模块
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional, Any, cast


def get_config_path() -> Path:
    """
    获取配置文件路径

    查找优先级：
    1. 当前工作目录: .smart-svn-commit.json
    2. 用户配置目录: ~/.config/smart-svn-commit/config.json (Linux/Mac)
    3. 用户配置目录: %APPDATA%/smart-svn-commit/config.json (Windows)
    4. 包内默认配置

    Returns:
        配置文件的完整路径（用户配置目录）
    """
    # 首先检查当前工作目录
    cwd_config = Path.cwd() / ".smart-svn-commit.json"
    if cwd_config.exists():
        return cwd_config

    # 用户配置目录
    if sys.platform == "win32":
        config_dir = Path.home() / "AppData" / "Roaming" / "smart-svn-commit"
    else:
        config_dir = Path.home() / ".config" / "smart-svn-commit"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置

    Returns:
        默认配置字典
    """
    return {
        "ignorePatterns": [
            ".DS_Store",
            "Thumbs.db",
            "*.tmp",
            "Library/",
            "Temp/",
            ".vs/",
            "obj/",
            "UserSettings/",
        ],
        "commitMessage": {
            "format": "conventional",
            "language": "zh",
            "types": ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "build"],
            "scopes": [
                "guild",
                "battle",
                "chat",
                "player",
                "ui",
                "network",
                "config",
                "art",
                "audio",
            ],
        },
        "ui": {"splitterRatio": [30, 70]},
        "aiApi": {
            "enabled": False,
            "baseUrl": "",
            "apiKey": "",
            "model": "gpt-3.5-turbo",
            "prompts": {
                "system": """你是一个专业的代码提交消息生成助手。请根据代码的 diff 内容生成符合 Conventional Commits 格式的提交消息。

格式要求：
- 格式：<类型>(<范围>): <简短描述>
- 类型（type）：feat（新功能）、fix（修复bug）、docs（文档）、style（格式）、refactor（重构）、perf（性能）、test（测试）、chore（构建/工具）
- 范围（scope）：根据文件路径和变更内容判断，如 ui、battle、player、network、config 等
- 描述：简洁明了地说明变更内容，使用中文

请只返回提交消息本身，不要包含任何解释或额外内容。""",
                "user": """请根据以下代码变更生成提交消息：

{diff_summary}

请直接返回提交消息，格式如：feat(battle): 添加新的战斗技能系统""",
            },
        },
    }


def load_config() -> Dict[str, Any]:
    """
    加载配置文件

    Returns:
        配置字典，如果不存在则返回默认配置
    """
    # 首先尝试当前工作目录配置
    cwd_config = Path.cwd() / ".smart-svn-commit.json"
    if cwd_config.exists():
        try:
            with open(cwd_config, "r", encoding="utf-8") as f:
                return cast(Dict[str, Any], json.load(f))
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告: 无法读取配置文件 {cwd_config}: {e}", file=sys.stderr)

    # 尝试用户配置目录
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return cast(Dict[str, Any], json.load(f))
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告: 无法读取配置文件 {config_path}: {e}", file=sys.stderr)

    # 返回默认配置
    return get_default_config()


def save_config(config: Dict[str, Any], config_path: Optional[Path] = None) -> bool:
    """
    保存配置文件

    Args:
        config: 配置字典
        config_path: 配置文件路径，如果为 None 则使用默认路径

    Returns:
        是否保存成功
    """
    if config_path is None:
        config_path = get_config_path()

    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"警告: 无法保存配置文件 {config_path}: {e}", file=sys.stderr)
        return False


def init_config() -> Path:
    """
    初始化配置文件（在用户配置目录创建默认配置）

    Returns:
        创建的配置文件路径
    """
    config_path = get_config_path()
    default_config = get_default_config()
    save_config(default_config, config_path)
    return config_path
