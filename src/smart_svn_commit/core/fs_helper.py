"""
文件系统操作辅助类
"""

import sys
import os
import subprocess
from pathlib import Path


class FileSystemHelper:
    """文件系统操作辅助类"""

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """直接删除文件系统中的文件

        Args:
            file_path: 文件路径

        Returns:
            是否删除成功
        """
        try:
            path_obj = Path(file_path)
            if path_obj.is_file():
                path_obj.unlink()
                return True
            elif path_obj.is_dir():
                path_obj.rmdir()
                return True
        except (FileNotFoundError, OSError) as e:
            print(f"无法删除文件: {e}", file=sys.stderr)
        return False

    @staticmethod
    def open_file(file_path: str) -> None:
        """使用系统默认程序打开文件

        Args:
            file_path: 文件路径
        """
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
        except (FileNotFoundError, OSError) as e:
            print(f"无法打开文件: {e}", file=sys.stderr)

    @staticmethod
    def open_containing_folder(file_path: str) -> None:
        """打开文件所在目录并选中文件

        Args:
            file_path: 文件路径
        """
        try:
            folder_path = str(Path(file_path).parent)
            if sys.platform == "win32":
                subprocess.run(["explorer", "/select,", file_path])
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", file_path])
            else:
                subprocess.run(["xdg-open", folder_path])
        except (FileNotFoundError, OSError) as e:
            print(f"无法打开目录: {e}", file=sys.stderr)
