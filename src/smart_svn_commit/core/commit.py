"""
SVN 提交执行模块
"""

import os
import re
import subprocess
import tempfile
from typing import Any

# 默认常量
SUCCESS_MESSAGE = "提交成功"
FAILURE_MESSAGE = "提交失败"
NO_FILES_MESSAGE = "没有选择要提交的文件"
REVISION_PATTERN = r"Committed revision (\d+)"


def execute_svn_commit(files: list[str], message: str) -> dict[str, Any]:
    """
    执行 SVN 提交命令

    Args:
        files: 要提交的文件列表
        message: 提交消息

    Returns:
        包含 success, revision, message, output 的字典
    """
    if not files:
        return {"success": False, "message": NO_FILES_MESSAGE, "output": ""}

    # 创建临时文件包含文件列表（SVN --targets 参数）
    # 使用 delete=False 以便在 Windows 上 SVN 可以读取文件
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False, suffix=".txt"
    ) as f:
        for file_path in files:
            f.write(file_path + "\n")
        targets_file = f.name

    try:
        result = subprocess.run(
            ["svn", "commit", "--targets", targets_file, "-m", message],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="ignore",
        )

        success = result.returncode == 0
        revision = _extract_revision(result.stdout) if success else None

        return {
            "success": success,
            "revision": revision,
            "message": SUCCESS_MESSAGE if success else FAILURE_MESSAGE,
            "output": result.stdout + result.stderr,
        }
    finally:
        # 确保删除临时文件，忽略错误（Windows 可能锁定文件）
        _safe_delete_file(targets_file)


def _extract_revision(output: str) -> str | None:
    """
    从 SVN 提交输出中提取修订版本号

    Args:
        output: SVN 命令输出

    Returns:
        修订版本号，未找到时返回 None
    """
    match = re.search(REVISION_PATTERN, output)
    return match.group(1) if match else None


def _safe_delete_file(file_path: str) -> None:
    """
    安全删除文件，忽略所有错误

    Args:
        file_path: 文件路径
    """
    try:
        os.unlink(file_path)
    except (FileNotFoundError, PermissionError, OSError):
        pass


def run_svn_status() -> list[tuple[str, str]]:
    """
    运行 svn status 命令并解析输出

    Returns:
        (状态, 文件路径) 元组列表
    """
    from .parser import parse_svn_status

    try:
        result = subprocess.run(
            ["svn", "status"],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="ignore",
        )
        if result.returncode == 0:
            return parse_svn_status(result.stdout)
    except (FileNotFoundError, OSError):
        pass

    return []
