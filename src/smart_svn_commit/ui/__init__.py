"""
UI 模块 - PyQt5 图形界面

此模块包含所有 PyQt5 相关的 GUI 组件。
"""

# 导入主函数（如果 PyQt5 可用）
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication

    from .main_window import show_quick_pick
    from .svn_loader import SVNStatusLoader

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

__all__ = ["show_quick_pick", "SVNStatusLoader", "PYQT5_AVAILABLE"]
