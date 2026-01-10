"""
AI 提交消息生成器
"""

import sys
from typing import Any, Dict, List

# OpenAI SDK 导入
try:
    from openai import OpenAI as OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..core.config import load_config

# 默认常量
DEFAULT_MESSAGE = "chore: 提交变更"
DEFAULT_MAX_DIFF_LENGTH = 2000
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 200
DEFAULT_TIMEOUT = 30.0

# 默认提示词
DEFAULT_SYSTEM_PROMPT = """你是一个专业的代码提交消息生成助手。请根据代码的 diff 内容生成符合 Conventional Commits 格式的提交消息。

格式要求：
- 格式：<类型>(<范围>): <简短描述>
- 类型：feat（新功能）、fix（修复bug）、docs（文档）、style（格式）、refactor（重构）、perf（性能）、test（测试）、chore（构建/工具）
- 范围：根据文件路径和变更内容判断，如 ui、battle、player、network、config 等
- 描述：简洁明了地说明变更内容，使用中文

请只返回提交消息本身，不要包含任何解释或额外内容。"""

DEFAULT_USER_TEMPLATE = """请根据以下代码变更生成提交消息：

{diff_summary}

请直接返回提交消息，格式如：feat(battle): 添加新的战斗技能系统"""


def generate_commit_message_with_ai(
    files_with_diff: List[Dict[str, str]], config: Dict[str, Any] | None = None
) -> str:
    """
    使用 OpenAI SDK 生成提交消息

    Args:
        files_with_diff: 包含 path 和 diff 的字典列表
        config: 配置字典（可选，如果为 None 则自动加载）

    Returns:
        生成的提交消息，如果失败则返回默认消息
    """
    if config is None:
        config = load_config()

    # 检查 API 配置
    api_config = config.get("aiApi", {})
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
    diff_summary = _build_diff_summary(files_with_diff)
    if not diff_summary:
        return DEFAULT_MESSAGE

    # 获取提示词
    prompts_config = api_config.get("prompts", {})
    system_prompt = prompts_config.get("system", DEFAULT_SYSTEM_PROMPT)
    user_template = prompts_config.get("user", DEFAULT_USER_TEMPLATE)
    user_prompt = user_template.format(diff_summary=diff_summary)

    # 调用 API
    return _call_openai_api(base_url, api_key, model, system_prompt, user_prompt)


def _build_diff_summary(files_with_diff: List[Dict[str, str]]) -> str:
    """
    构建 diff 摘要字符串

    Args:
        files_with_diff: 包含 path 和 diff 的字典列表

    Returns:
        diff 摘要字符串
    """
    diff_parts = []
    for file_info in files_with_diff:
        diff = file_info.get("diff", "")
        if diff:
            path = file_info.get("path", "")
            truncated_diff = diff[:DEFAULT_MAX_DIFF_LENGTH]
            diff_parts.append(f"文件: {path}\n变更内容:\n{truncated_diff}")

    return "\n\n".join(diff_parts)


def _call_openai_api(
    base_url: str, api_key: str, model: str, system_prompt: str, user_prompt: str
) -> str:
    """
    调用 OpenAI API 生成提交消息

    Args:
        base_url: API 基础 URL
        api_key: API 密钥
        model: 模型名称
        system_prompt: 系统提示词
        user_prompt: 用户提示词

    Returns:
        生成的提交消息，失败时返回默认消息
    """
    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            timeout=DEFAULT_TIMEOUT,
        )

        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content
            message = content.strip("\"'").strip()
            if message:
                return message

    except (ConnectionError, TimeoutError) as e:
        print(f"API 网络错误: {e}", file=sys.stderr)
    except OSError as e:
        print(f"API 系统错误: {e}", file=sys.stderr)
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "Not Found" in error_msg:
            print(f"API 端点错误 (404): 请检查 base_url 配置，当前值: {base_url}", file=sys.stderr)
        else:
            print(f"API 调用失败: {error_msg}", file=sys.stderr)

    return DEFAULT_MESSAGE
