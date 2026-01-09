"""
右键菜单构建器模块
"""

from typing import TYPE_CHECKING
from PyQt5.QtWidgets import QMenu, QAction, QWidget
from PyQt5.QtCore import Qt

from .menu_constants import (
    MenuAction,
    STATUS_MENU_ACTIONS,
    COMMON_MENU_ACTIONS,
    FILE_MENU_ACTIONS,
    MENU_ACTION_LABELS,
    MENU_ACTION_ICONS,
)

if TYPE_CHECKING:
    from ..core.svn_executor import SVNCommandExecutor
    from ..core.fs_helper import FileSystemHelper


class ContextMenuBuilder:
    """右键菜单构建器 - 根据文件状态动态构建菜单"""

    # 分隔符位置配置
    SEPARATOR_AFTER_ACTIONS = {MenuAction.BLAME, MenuAction.DELETE, MenuAction.DELETE_FILE}

    # 需要刷新状态的操作
    REFRESH_ACTIONS = {MenuAction.REVERT, MenuAction.ADD, MenuAction.DELETE, MenuAction.DELETE_FILE}

    def __init__(
        self,
        svn_executor: "SVNCommandExecutor",
        fs_helper: "FileSystemHelper",
        parent_widget: QWidget,
        refresh_callback=None,
    ):
        self._svn_executor = svn_executor
        self._fs_helper = fs_helper
        self._parent = parent_widget
        self._style = parent_widget.style()
        self._refresh_callback = refresh_callback

    def build_menu(self, file_path: str, status: str, parent: QWidget) -> QMenu:
        """
        构建右键上下文菜单

        Args:
            file_path: 文件路径
            status: SVN 状态码
            parent: 父控件

        Returns:
            构建好的菜单
        """
        menu = QMenu()

        # 获取该状态对应的菜单操作
        actions = STATUS_MENU_ACTIONS.get(status, COMMON_MENU_ACTIONS)

        # 添加 SVN 操作
        for action in actions:
            self._add_menu_action(menu, action, file_path)

        # 添加分隔符和文件操作
        menu.addSeparator()
        for action in FILE_MENU_ACTIONS:
            self._add_menu_action(menu, action, file_path)

        return menu

    def _add_menu_action(self, menu: QMenu, action: str, file_path: str) -> None:
        """
        添加单个菜单项（消除重复代码）

        Args:
            menu: 菜单对象
            action: 操作类型
            file_path: 文件路径
        """
        menu_action = QAction(MENU_ACTION_LABELS[action], menu)

        # 设置图标
        icon_standard_pixmap = MENU_ACTION_ICONS.get(action)
        if icon_standard_pixmap is not None:
            icon = self._style.standardIcon(icon_standard_pixmap)
            menu_action.setIcon(icon)

        # 连接信号
        menu_action.triggered.connect(
            lambda checked, a=action, p=file_path: self._execute_action(a, p)
        )

        menu.addAction(menu_action)

        # 在特定位置添加分隔符
        if action in self.SEPARATOR_AFTER_ACTIONS:
            menu.addSeparator()

    def _execute_action(self, action: str, file_path: str) -> None:
        """执行菜单操作"""
        action_handlers = {
            MenuAction.DIFF: self._svn_executor.diff,
            MenuAction.LOG: self._svn_executor.log,
            MenuAction.BLAME: self._svn_executor.blame,
            MenuAction.REVERT: self._svn_executor.revert,
            MenuAction.ADD: self._svn_executor.add,
            MenuAction.DELETE: self._svn_executor.delete,
            MenuAction.DELETE_FILE: self._fs_helper.delete_file,
            MenuAction.OPEN_FILE: self._fs_helper.open_file,
            MenuAction.OPEN_FOLDER: self._fs_helper.open_containing_folder,
        }

        handler = action_handlers.get(action)
        if handler:
            result = handler(file_path)
            # 对于修改操作，检查返回值并触发刷新
            if action in self.REFRESH_ACTIONS:
                # 如果操作是同步的（有返回值），检查是否成功
                should_refresh = result is True or result is None
                if should_refresh and self._refresh_callback:
                    self._refresh_callback()
