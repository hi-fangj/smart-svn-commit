"""
提交消息生成模块（UI 专用）
"""

import subprocess
import sys
from typing import List, Dict, Any, cast

# OpenAI SDK 导入
try:
    from openai import OpenAI as OpenAIClient

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..core.config import load_config


def get_file_diff(file_path: str) -> str:
    """
    获取文件的 SVN diff 内容。

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


def generate_commit_message_with_ai(
    files_with_diff: List[Dict[str, str]], config: Dict[str, Any]
) -> str:
    """
    使用 OpenAI SDK 生成提交消息。

    Args:
        files_with_diff: 包含 path 和 diff 的字典列表
        config: 配置字典

    Returns:
        生成的提交消息，如果失败则返回默认消息
    """
    DEFAULT_MESSAGE = "chore: 提交变更"
    api_config = config.get("aiApi", {})

    # 检查 API 配置
    if not api_config.get("enabled", False):
        return DEFAULT_MESSAGE

    if not OPENAI_AVAILABLE:
        print("OpenAI SDK 未安装，请运行: pip install openai", file=sys.stderr)
        return DEFAULT_MESSAGE

    base_url = api_config.get("baseUrl", "")
    api_key = api_config.get("apiKey", "")
    model = api_config.get("model", "gpt-3.5-turbo")

    if not base_url or not api_key:
        return DEFAULT_MESSAGE

    # 构建 diff 摘要
    diff_summary = "\n\n".join(
        [
            f"文件: {f['path']}\n变更内容:\n{f['diff'][:2000]}"
            for f in files_with_diff
            if f.get("diff")
        ]
    )

    if not diff_summary:
        return DEFAULT_MESSAGE

    # 从配置读取提示词，或使用默认值
    prompts_config = api_config.get("prompts", {})

    default_system_prompt = """你是一个专业的代码提交消息生成助手。请根据代码的 diff 内容生成符合 Conventional Commits 格式的提交消息。

格式要求：
- 格式：<类型>(<范围>): <简短描述>
- 类型（type）：feat（新功能）、fix（修复bug）、docs（文档）、style（格式）、refactor（重构）、perf（性能）、test（测试）、chore（构建/工具）
- 范围（scope）：根据文件路径和变更内容判断，如 ui、battle、player、network、config 等
- 描述：简洁明了地说明变更内容，使用中文

请只返回提交消息本身，不要包含任何解释或额外内容。"""

    default_user_template = """请根据以下代码变更生成提交消息：

{diff_summary}

请直接返回提交消息，格式如：feat(battle): 添加新的战斗技能系统"""

    system_prompt = prompts_config.get("system", default_system_prompt)
    user_template = prompts_config.get("user", default_user_template)
    user_prompt = user_template.format(diff_summary=diff_summary)

    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=200,
            timeout=30.0,
        )

        if response.choices and response.choices[0].message.content:
            content = cast(str, response.choices[0].message.content)
            message = content.strip("\"'").strip()
            if message:
                return message

    except (ConnectionError, TimeoutError) as e:
        # 网络连接相关错误
        print(f"API 网络错误: {e}", file=sys.stderr)
    except OSError as e:
        # 系统/IO 相关错误
        print(f"API 系统错误: {e}", file=sys.stderr)
    except Exception as e:
        # 其他未预期的错误
        error_msg = str(e)
        if "404" in error_msg or "Not Found" in error_msg:
            print(f"API 端点错误 (404): 请检查 base_url 配置，当前值: {base_url}", file=sys.stderr)
        else:
            print(f"API 调用失败: {error_msg}", file=sys.stderr)

    return DEFAULT_MESSAGE


def _generate_commit_message_by_keywords(files: List[str]) -> str:
    """
    基于文件路径关键词生成提交消息（降级方案）。

    Args:
        files: 选中的文件路径列表

    Returns:
        生成的提交消息字符串
    """
    from typing import Dict

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
        detected_type = None
        for type_name, patterns in path_type_patterns.items():
            if any(p in path_lower for p in patterns):
                detected_type = type_name
                break
        if detected_type:
            type_counts[detected_type] = type_counts.get(detected_type, 0) + 1

        # 检测范围
        detected_scope = None
        for scope_name, patterns in path_scope_patterns.items():
            if any(p in path_lower for p in patterns):
                detected_scope = scope_name
                break
        if detected_scope:
            scope_counts[detected_scope] = scope_counts.get(detected_scope, 0) + 1

    # 选择最常见的类型和范围
    commit_type = max(type_counts, key=lambda k: type_counts[k]) if type_counts else "chore"
    commit_scope = max(scope_counts, key=lambda k: scope_counts[k]) if scope_counts else ""

    # 构建提交消息
    if commit_scope:
        return f"{commit_type}({commit_scope}): 提交变更"
    else:
        return f"{commit_type}: 提交变更"


def generate_commit_message(files: List[str]) -> str:
    """
    根据选中的文件生成 Conventional Commits 格式的提交消息。
    优先使用 AI API，如果 API 未配置或失败，则降级到关键词匹配。

    Args:
        files: 选中的文件路径列表

    Returns:
        生成的提交消息字符串
    """
    if not files:
        return "chore: 提交变更"

    config = load_config()

    # 尝试使用 AI API 生成
    files_with_diff = []
    for file_path in files:
        diff_content = get_file_diff(file_path)
        files_with_diff.append({"path": file_path, "diff": diff_content})

    # 尝试 API 生成
    api_message = generate_commit_message_with_ai(files_with_diff, config)
    if api_message != "chore: 提交变更":
        return api_message

    # 降级到关键词匹配
    return _generate_commit_message_by_keywords(files)
