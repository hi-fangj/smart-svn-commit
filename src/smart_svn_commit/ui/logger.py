"""
日志系统模块
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class UILogger:
    """GUI应用专用日志系统"""

    _instance: Optional["UILogger"] = None
    _logger: Optional[logging.Logger] = None
    _log_file: Optional[Path] = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化日志系统"""
        if self._logger is not None:
            return

        # 创建日志目录
        log_dir = Path.home() / ".smart-svn-commit" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # 设置日志文件路径
        self._log_file = log_dir / "ui_debug.log"

        # 创建logger
        self._logger = logging.getLogger("smart_svn_commit.ui")
        self._logger.setLevel(logging.DEBUG)

        # 清除已有的handlers
        self._logger.handlers.clear()

        # 文件handler - 详细日志
        file_handler = logging.FileHandler(self._log_file, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)

        # 控制台handler - 简化日志
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)

        # 记录启动信息
        self.info("=" * 60)
        self.info("SVN提交助手 UI 启动")
        self.info(f"日志文件路径: {self._log_file}")
        self.info("=" * 60)

    def debug(self, message: str) -> None:
        """调试级别日志"""
        if self._logger:
            self._logger.debug(message)

    def info(self, message: str) -> None:
        """信息级别日志"""
        if self._logger:
            self._logger.info(message)

    def warning(self, message: str) -> None:
        """警告级别日志"""
        if self._logger:
            self._logger.warning(message)

    def error(self, message: str) -> None:
        """错误级别日志"""
        if self._logger:
            self._logger.error(message)

    def get_log_file_path(self) -> Optional[Path]:
        """获取日志文件路径"""
        return self._log_file


# 创建全局logger实例
ui_logger = UILogger()
