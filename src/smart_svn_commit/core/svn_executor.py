"""
SVN 命令执行器 - 统一处理所有 SVN 相关操作
"""

import subprocess
import sys

# TortoiseProc 命令前缀
TORTOISE_PROC = "TortoiseProc.exe"
TORTOISE_PATH_ARG = "/path:"

# 命令映射
TORTOISE_COMMANDS = {
    "diff": "/command:diff",
    "log": "/command:log",
    "blame": "/command:blame",
    "revert": "/command:revert",
    "add": "/command:add",
    "delete": "/command:remove",
}

SVN_COMMANDS = {
    "diff": "diff",
    "log": "log",
    "blame": "blame",
    "revert": "revert",
    "add": "add",
    "delete": "delete",
}

# 修改类命令（需要等待结果）
MODIFYING_COMMANDS = {"revert", "add", "delete"}


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

    def _run_svn_command(self, svn_cmd: str, file_path: str) -> bool | None:
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

    def _execute_command(self, operation: str, file_path: str) -> bool | None:
        """
        执行 SVN 操作（统一入口）

        Args:
            operation: 操作名称
            file_path: 文件路径

        Returns:
            None 对于异步命令，True/False 对于同步命令
        """
        tortoise_cmd = TORTOISE_COMMANDS.get(operation, "")
        if self._try_tortoise(tortoise_cmd, file_path):
            return True

        svn_cmd = SVN_COMMANDS.get(operation, "")
        if operation in MODIFYING_COMMANDS:
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
