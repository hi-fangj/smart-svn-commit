"""
SVN 提交执行模块
"""

import sys
import os
import re
import subprocess
import tempfile
from typing import List, Dict, Any


def execute_svn_commit(files: List[str], message: str) -> Dict[str, Any]:
    """
    执行 SVN 提交命令

    Args:
        files: 要提交的文件列表
        message: 提交消息

    Returns:
        包含 success, revision, message, output 的字典
    """
    if not files:
        return {"success": False, "message": "没有选择要提交的文件", "output": ""}

    # 创建临时文件包含文件列表（SVN --targets 参数）
    # 使用 delete=False 以便在 Windows 上 SVN 可以读取文件
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
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

        # 解析输出获取修订版本号
        revision = None
        if result.returncode == 0:
            # SVN 成功输出格式: "Committed revision 12345."
            match = re.search(r"Committed revision (\d+)", result.stdout)
            if match:
                revision = match.group(1)

        return {
            "success": result.returncode == 0,
            "revision": revision,
            "message": "提交成功" if result.returncode == 0 else "提交失败",
            "output": result.stdout + result.stderr,
        }
    finally:
        # 确保删除临时文件，忽略错误（Windows 可能锁定文件）
        try:
            os.unlink(targets_file)
        except (FileNotFoundError, PermissionError, OSError):
            pass


def run_svn_status() -> List[tuple]:
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
