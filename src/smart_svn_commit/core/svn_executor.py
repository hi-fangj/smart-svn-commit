"""
SVN 命令执行器 - 统一处理所有 SVN 相关操作
"""

import subprocess
import sys
from typing import Optional


class SVNCommandExecutor:
    """SVN 命令执行器"""

    def __init__(self):
        self._is_windows = sys.platform == "win32"

    def _try_tortoise(self, command: str, file_path: str) -> bool:
        """尝试使用 TortoiseProc，返回是否成功"""
        if not self._is_windows:
            return False
        try:
            subprocess.Popen(["TortoiseProc.exe", command, "/path:" + file_path])
            return True
        except (FileNotFoundError, OSError):
            return False

    def execute_command(self, file_path: str, svn_cmd: str, tortoise_cmd: str) -> None:
        """执行 SVN 命令"""
        if not self._try_tortoise(tortoise_cmd, file_path):
            try:
                subprocess.Popen(["svn", svn_cmd, file_path])
            except (FileNotFoundError, OSError) as e:
                print(f"无法执行 SVN 命令: {e}", file=sys.stderr)

    def execute_modifying_command(
        self, file_path: str, svn_cmd: str, tortoise_cmd: str, action_name: str
    ) -> bool:
        """执行修改类 SVN 命令（使用 subprocess.run）"""
        if not self._try_tortoise(tortoise_cmd, file_path):
            try:
                result = subprocess.run(
                    ["svn", svn_cmd, file_path], check=False, capture_output=True
                )
                return result.returncode == 0
            except (FileNotFoundError, OSError) as e:
                print(f"无法{action_name}文件: {e}", file=sys.stderr)
                return False
        return True

    def diff(self, file_path: str) -> None:
        """查看文件差异"""
        self.execute_command(file_path, "diff", "/command:diff")

    def log(self, file_path: str) -> None:
        """查看文件日志"""
        self.execute_command(file_path, "log", "/command:log")

    def blame(self, file_path: str) -> None:
        """查看文件注释"""
        self.execute_command(file_path, "blame", "/command:blame")

    def revert(self, file_path: str) -> bool:
        """还原文件"""
        return self.execute_modifying_command(
            file_path, "revert", "/command:revert", "还原"
        )

    def add(self, file_path: str) -> bool:
        """添加文件到版本控制"""
        return self.execute_modifying_command(file_path, "add", "/command:add", "添加")

    def delete(self, file_path: str) -> bool:
        """从版本控制中删除文件"""
        return self.execute_modifying_command(
            file_path, "delete", "/command:remove", "删除"
        )
