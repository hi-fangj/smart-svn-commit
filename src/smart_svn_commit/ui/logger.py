"""
日志系统模块
"""

import logging
import sys
import traceback
from pathlib import Path
from typing import Optional


class UILogger:
    """GUI应用专用日志系统"""

    _instance: Optional["UILogger"] = None
    _logger: Optional[logging.Logger] = None
    _log_file: Optional[Path] = None
    _initialized = False

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化日志系统"""
        if self._initialized:
            return

        try:
            # 创建日志目录
            log_dir = Path.home() / ".smart-svn-commit" / "logs"
            print(f"[Logger] 尝试创建日志目录: {log_dir}", file=sys.stderr)
            log_dir.mkdir(parents=True, exist_ok=True)

            # 设置日志文件路径
            self._log_file = log_dir / "ui_debug.log"
            print(f"[Logger] 日志文件路径: {self._log_file}", file=sys.stderr)

            # 创建logger
            self._logger = logging.getLogger("smart_svn_commit.ui")
            self._logger.setLevel(logging.DEBUG)

            # 清除已有的handlers
            self._logger.handlers.clear()

            # 文件handler - 详细日志
            file_handler = logging.FileHandler(
                self._log_file, mode="w", encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)
            print(f"[Logger] 文件handler已添加: {file_handler}", file=sys.stderr)

            # 控制台handler - 简化日志
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)
            print(f"[Logger] 控制台handler已添加: {console_handler}", file=sys.stderr)

            # 标记为已初始化
            self._initialized = True

            # 记录启动信息
            self.info("=" * 60)
            self.info("SVN提交助手 UI 启动")
            self.info(f"日志文件路径: {self._log_file}")
            self.info(f"日志目录: {log_dir}")
            self.info("=" * 60)

            print(f"[Logger] 日志系统初始化成功!", file=sys.stderr)

        except Exception as e:
            print(f"[Logger] 日志系统初始化失败: {e}", file=sys.stderr)
            print(f"[Logger] 错误详情: {traceback.format_exc()}", file=sys.stderr)
            # 即使失败也标记为已初始化，避免重复尝试
            self._initialized = True
            raise

    def debug(self, message: str) -> None:
        """调试级别日志"""
        try:
            if self._logger:
                self._logger.debug(message)
            else:
                print(f"[DEBUG] {message}", file=sys.stderr)
        except Exception as e:
            print(f"[Logger.debug] 错误: {e}, 消息: {message}", file=sys.stderr)

    def info(self, message: str) -> None:
        """信息级别日志"""
        try:
            if self._logger:
                self._logger.info(message)
            else:
                print(f"[INFO] {message}", file=sys.stderr)
        except Exception as e:
            print(f"[Logger.info] 错误: {e}, 消息: {message}", file=sys.stderr)

    def warning(self, message: str) -> None:
        """警告级别日志"""
        try:
            if self._logger:
                self._logger.warning(message)
            else:
                print(f"[WARNING] {message}", file=sys.stderr)
        except Exception as e:
            print(f"[Logger.warning] 错误: {e}, 消息: {message}", file=sys.stderr)

    def error(self, message: str) -> None:
        """错误级别日志"""
        try:
            if self._logger:
                self._logger.error(message)
            else:
                print(f"[ERROR] {message}", file=sys.stderr)
        except Exception as e:
            print(f"[Logger.error] 错误: {e}, 消息: {message}", file=sys.stderr)

    def get_log_file_path(self) -> Optional[Path]:
        """获取日志文件路径"""
        return self._log_file


# 创建全局logger实例
try:
    ui_logger = UILogger()
    print("[main] ui_logger 实例创建成功", file=sys.stderr)
except Exception as e:
    print(f"[main] ui_logger 实例创建失败: {e}", file=sys.stderr)
    print(f"[main] 错误详情: {traceback.format_exc()}", file=sys.stderr)
    # 创建一个简单的回退logger
    ui_logger = UILogger.__new__(UILogger)
    ui_logger._logger = None
    ui_logger._log_file = None
    ui_logger._initialized = False
