"""
SVN 状态异步加载器模块

使用 PyQt5 QThread 在后台线程中执行 SVN 状态查询，避免阻塞 UI。
"""

from typing import List, Tuple, Optional
from PyQt5.QtCore import QThread, pyqtSignal

from ..core.commit import run_svn_status
from ..core.config import load_config
from ..utils.filters import apply_ignore_patterns


class SVNStatusLoader(QThread):
    """
    SVN 状态加载工作线程

    在后台线程中执行 svn status 命令，完成后通过信号通知主线程更新 UI。

    Signals:
        finished: 加载成功时发送，参数为文件列表
        error: 加载失败时发送，参数为错误消息
    """

    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """
        初始化加载器

        Args:
            parent: 父对象
        """
        super().__init__(parent)

    def run(self) -> None:
        """
        执行 SVN 状态查询

        此方法在后台线程中运行，完成后发送 finished 或 error 信号。
        """
        try:
            # 执行 svn status 命令
            files: List[Tuple[str, str]] = run_svn_status()

            # 应用忽略模式
            config = load_config()
            ignore_patterns = config.get("ignorePatterns", [])
            files = apply_ignore_patterns(files, ignore_patterns)

            # 发送成功信号
            self.finished.emit(files)
        except Exception as e:
            # 发送错误信号
            self.error.emit(f"加载 SVN 状态失败: {str(e)}")
