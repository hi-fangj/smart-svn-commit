"""
SVN 命令执行器 - 统一处理所有 SVN 相关操作
"""

import subprocess
import sys
from typing import Any, Dict, Optional

# TortoiseProc 命令前缀
TORTOISE_PROC = "TortoiseProc.exe"
TORTOISE_PATH_ARG = "/path:"


# 命令配置（合并 Tortoise 和 SVN 命令映射）
COMMAND_CONFIG: Dict[str, Dict[str, Any]] = {
    "diff": {"tortoise": "/command:diff", "svn": "diff", "modifying": False},
    "log": {"tortoise": "/command:log", "svn": "log", "modifying": False},
    "blame": {"tortoise": "/command:blame", "svn": "blame", "modifying": False},
    "revert": {"tortoise": "/command:revert", "svn": "revert", "modifying": True},
    "add": {"tortoise": "/command:add", "svn": "add", "modifying": True},
    "delete": {"tortoise": "/command:remove", "svn": "delete", "modifying": True},
}


class SVNCommandExecutor:
    """SVN 命令执行器"""

    def __init__(self):
        self._is_windows = sys.platform == "win32"

    def _try_tortoise(self, command: str, file_path: str) -> bool:
        """尝试使用 TortoiseProc，返回是否成功"""
        if not self._is_windows:
            return False
        try:
            subprocess.Popen([TORTOISE_PROC, command, f"{TORTOISE_PATH_ARG}{file_path}"])
            return True
        except (FileNotFoundError, OSError):
            return False

    def _run_svn_command(self, svn_cmd: str, file_path: str) -> Optional[bool]:
        """
        运行 SVN 命令

        Args:
            svn_cmd: SVN 命令
            file_path: 文件路径

        Returns:
            None 对于异步命令，True/False 对于同步命令
        """
        try:
            result = subprocess.run(
                ["svn", svn_cmd, file_path],
                check=False,
                capture_output=True,
            )
            return result.returncode == 0
        except (FileNotFoundError, OSError) as e:
            print(f"无法执行 SVN 命令: {e}", file=sys.stderr)
            return False

    def _execute_command(self, operation: str, file_path: str) -> Optional[bool]:
        """
        执行 SVN 操作（统一入口）

        Args:
            operation: 操作名称
            file_path: 文件路径

        Returns:
            None 对于异步命令，True/False 对于同步命令
        """
        config = COMMAND_CONFIG.get(operation, {})
        tortoise_cmd = config.get("tortoise", "")
        svn_cmd = config.get("svn", "")
        is_modifying = config.get("modifying", False)

        if self._try_tortoise(tortoise_cmd, file_path):
            return True

        if is_modifying:
            return self._run_svn_command(svn_cmd, file_path)
        else:
            self._run_svn_command(svn_cmd, file_path)
            return None

    def diff(self, file_path: str) -> None:
        """查看文件差异"""
        self._execute_command("diff", file_path)

    def log(self, file_path: str) -> None:
        """查看文件日志"""
        self._execute_command("log", file_path)

    def blame(self, file_path: str) -> None:
        """查看文件注释"""
        self._execute_command("blame", file_path)

    def revert(self, file_path: str) -> bool:
        """还原文件"""
        result = self._execute_command("revert", file_path)
        return result is True

    def add(self, file_path: str) -> bool:
        """添加文件到版本控制"""
        result = self._execute_command("add", file_path)
        return result is True

    def delete(self, file_path: str) -> bool:
        """从版本控制中删除文件"""
        result = self._execute_command("delete", file_path)
        return result is True
