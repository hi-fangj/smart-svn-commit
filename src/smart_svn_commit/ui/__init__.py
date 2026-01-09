"""
UI 模块 - PyQt5 图形界面

此模块包含所有 PyQt5 相关的 GUI 组件。
"""

# 尝试导入 PyQt5
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

# 导入主函数（如果 PyQt5 可用）
if PYQT5_AVAILABLE:
    from .main_window import show_quick_pick

__all__ = ["show_quick_pick", "PYQT5_AVAILABLE"]
