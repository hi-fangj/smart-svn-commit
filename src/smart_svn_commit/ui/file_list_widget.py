"""
文件列表控件模块
"""

import sys
from typing import List, Optional, Set, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QGuiApplication
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from smart_svn_commit.utils.regex_cache import get_global_cache
from smart_svn_commit.core.parser import extract_path_from_display_text

from .constants import (
    CANDIDATE_BG_COLOR,
    CHECKBOX_COLUMN,
    PATH_COLUMN,
    STATUS_COLORS,
)


class FileListWidget:
    """带复选框的文件列表控件"""

    def __init__(self, parent=None):
        if not sys.modules.get("PyQt5.QtWidgets"):
            raise RuntimeError("PyQt5 未安装")

        self.tree = QTreeWidget(parent)
        self._setup_tree()
        self._regex_cache = get_global_cache()

        # 缓存颜色画刷，避免重复创建
        self._color_brushes = {
            color: QBrush(QColor(color)) for color in STATUS_COLORS.values()
        }

        # 备选范围相关
        self.candidate_indices: Set[int] = set()
        self.shift_start_index: int = -1

        # 缓存备选背景色，避免重复创建
        self._candidate_bg = QBrush(QColor(CANDIDATE_BG_COLOR))
        self._default_bg = QBrush()

    def _setup_tree(self) -> None:
        """初始化树控件配置"""
        self.tree.setHeaderLabels(["", "文件路径"])
        self.tree.setColumnWidth(CHECKBOX_COLUMN, 30)
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(False)

    def add_item(self, status: str, path: str) -> None:
        """添加文件项"""
        tree_item = QTreeWidgetItem()
        tree_item.setFlags(tree_item.flags() | Qt.ItemIsUserCheckable)
        tree_item.setCheckState(CHECKBOX_COLUMN, Qt.Unchecked)

        # 设置状态文字和路径
        tree_item.setText(PATH_COLUMN, f"[{status}] {path}")

        # 使用状态颜色作为字体颜色
        color = STATUS_COLORS.get(status, "#000000")
        tree_item.setForeground(PATH_COLUMN, self._color_brushes[color])

        self.tree.addTopLevelItem(tree_item)

    def get_checked_items(self) -> List[str]:
        """获取选中的文件路径"""
        checked_paths = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(CHECKBOX_COLUMN) == Qt.Checked:
                path = extract_path_from_display_text(item.text(PATH_COLUMN))
                if path:
                    checked_paths.append(path)
        return checked_paths

    def _set_all_check_state(self, state: Qt.CheckState) -> None:
        """设置所有项的复选框状态（内部辅助方法）"""
        self.tree.blockSignals(True)
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setCheckState(CHECKBOX_COLUMN, state)
        self.tree.blockSignals(False)

    def select_all(self) -> None:
        """全选"""
        self._set_all_check_state(Qt.Checked)

    def clear_selection(self) -> None:
        """清空选择"""
        self._set_all_check_state(Qt.Unchecked)

    def invert_selection(self) -> None:
        """反选"""
        self.tree.blockSignals(True)
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            new_state = (
                Qt.Unchecked
                if item.checkState(CHECKBOX_COLUMN) == Qt.Checked
                else Qt.Checked
            )
            item.setCheckState(CHECKBOX_COLUMN, new_state)
        self.tree.blockSignals(False)

    def filter_by_text(
        self, search_text: str, all_items_data: List[Tuple[str, str]]
    ) -> None:
        """
        根据搜索文本过滤（支持多种模式）

        过滤模式：
        - 普通文本：大小写不敏感的包含匹配
        - 通配符：*.cs 匹配所有 .cs 文件，Test*.cs 匹配以 Test 开头的 .cs 文件
        """
        # 先保存当前选中状态
        checked_paths = set(self.get_checked_items())

        self.tree.clear()

        # 根据搜索文本过滤
        if search_text:
            filtered = self._apply_filter(search_text, all_items_data)
        else:
            filtered = all_items_data

        # 重新添加项并恢复选中状态
        for status, path in filtered:
            self.add_item(status, path)
            # 恢复选中状态
            if path in checked_paths:
                self.tree.topLevelItem(self.tree.topLevelItemCount() - 1).setCheckState(
                    CHECKBOX_COLUMN, Qt.Checked
                )

    def _apply_filter(
        self, search_text: str, items: List[Tuple[str, str]]
    ) -> List[Tuple[str, str]]:
        """
        应用过滤规则

        Args:
            search_text: 搜索文本（支持通配符）
            items: 原始项目列表

        Returns:
            过滤后的项目列表
        """
        # 检查是否为通配符模式：*.ext 或 *text 或 text*
        if "*" in search_text or "?" in search_text:
            return self._wildcard_filter(search_text, items)
        else:
            return self._text_filter(search_text, items)

    def _wildcard_filter(
        self, pattern: str, items: List[Tuple[str, str]]
    ) -> List[Tuple[str, str]]:
        """
        使用通配符过滤（委托给 utils.filters 模块）

        支持的通配符模式：
        - *.cs : 匹配所有 .cs 文件
        - Test*.cs : 匹配以 Test 开头且以 .cs 结尾的文件
        - *Test : 匹配以 Test 结尾的文件
        - *.cs* : 匹配包含 .cs 的文件

        Args:
            pattern: 通配符模式
            items: 原始项目列表

        Returns:
            过滤后的项目列表
        """
        from smart_svn_commit.utils.filters import wildcard_filter

        return wildcard_filter(pattern, items)

    def _text_filter(
        self, search_text: str, items: List[Tuple[str, str]]
    ) -> List[Tuple[str, str]]:
        """
        使用普通文本过滤（大小写不敏感）

        Args:
            search_text: 搜索文本
            items: 原始项目列表

        Returns:
            过滤后的项目列表
        """
        from smart_svn_commit.utils.filters import text_filter

        return text_filter(search_text, items)

    def count(self) -> int:
        """返回项数"""
        return int(self.tree.topLevelItemCount())

    def get_widget(self) -> QTreeWidget:
        """获取底层控件"""
        return self.tree

    def sort_items(self, sort_by: str, ascending: bool = True) -> None:
        """
        对列表项进行排序

        Args:
            sort_by: 排序字段，'path'（路径）、'ext'（后缀）、'status'（状态）
            ascending: 是否升序
        """
        # 收集所有项
        items_data = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            display_text = item.text(PATH_COLUMN)
            status = (
                display_text[1]
                if len(display_text) > 1 and display_text[0] == "["
                else ""
            )
            path = extract_path_from_display_text(display_text)
            check_state = item.checkState(CHECKBOX_COLUMN)
            items_data.append((status, path, check_state))

        # 根据排序字段进行排序
        if sort_by == "path":
            items_data.sort(key=lambda x: x[1] or "", reverse=not ascending)
        elif sort_by == "ext":
            # 按后缀排序，无后缀的排在最后
            def get_ext(item):
                path = item[1]
                if not path:
                    return "~"
                dot_idx = path.rfind(".")
                if dot_idx > path.rfind("/"):
                    return path[dot_idx + 1 :].lower()
                return "~"  # 无后缀的排在最后

            items_data.sort(key=get_ext, reverse=not ascending)
        elif sort_by == "status":
            # 按状态码排序
            items_data.sort(key=lambda x: x[0] or "", reverse=not ascending)

        # 清空并重新添加排序后的项
        self.tree.blockSignals(True)
        self.tree.clear()
        for status, path, check_state in items_data:
            if path:
                self.add_item(status, path)
            # 恢复选中状态
            if self.tree.topLevelItemCount() > 0:
                last_item = self.tree.topLevelItem(self.tree.topLevelItemCount() - 1)
                last_item.setCheckState(CHECKBOX_COLUMN, check_state)
        self.tree.blockSignals(False)

    def update_candidate_highlight(self) -> None:
        """更新备选项的高亮显示"""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item:
                bg = (
                    self._candidate_bg
                    if i in self.candidate_indices
                    else self._default_bg
                )
                item.setBackground(PATH_COLUMN, bg)

    def clear_candidates(self) -> None:
        """清空备选项"""
        if self.candidate_indices:
            self.candidate_indices.clear()
            self.update_candidate_highlight()
        self.shift_start_index = -1

    def handle_item_click(
        self, index: int, new_state: Qt.CheckState, is_checkbox: bool = True
    ) -> None:
        """
        处理复选框状态改变，支持 Shift 批量选择

        Args:
            index: 项索引
            new_state: 新的复选框状态
            is_checkbox: 是否来自复选框点击
        """
        if is_checkbox:
            self._handle_checkbox_click(index, new_state)
        else:
            self._handle_path_click(index)

    def _handle_checkbox_click(self, index: int, new_state: Qt.CheckState) -> None:
        """处理复选框点击"""
        self.tree.blockSignals(True)

        if self.candidate_indices:
            # 应用状态到所有备选项
            for i in self.candidate_indices:
                item = self.tree.topLevelItem(i)
                if item:
                    item.setCheckState(CHECKBOX_COLUMN, new_state)
        else:
            # 只设置当前项
            item = self.tree.topLevelItem(index)
            if item:
                item.setCheckState(CHECKBOX_COLUMN, new_state)

        self.tree.blockSignals(False)

    def _handle_path_click(self, index: int) -> None:
        """处理路径列点击"""
        if QGuiApplication.keyboardModifiers() & Qt.ShiftModifier:
            self._handle_shift_click(index)
        else:
            # 普通路径点击：将当前路径设为备选项
            self.candidate_indices.clear()
            self.candidate_indices.add(index)
            self.update_candidate_highlight()
            self.shift_start_index = -1

    def _handle_shift_click(self, index: int) -> None:
        """处理 Shift+路径点击"""
        if self.candidate_indices:
            # 已有备选项：扩展范围
            start = min(self.candidate_indices)
            if start != index:
                start, end = min(start, index), max(start, index)
                self.candidate_indices = set(range(start, end + 1))
                self.update_candidate_highlight()
        elif self.shift_start_index < 0:
            # 第一次 Shift 点击：记录起点
            self.shift_start_index = index
        else:
            # 第二次 Shift 点击：创建备选范围
            if self.shift_start_index != index:
                start, end = (
                    min(self.shift_start_index, index),
                    max(self.shift_start_index, index),
                )
                self.candidate_indices = set(range(start, end + 1))
                self.update_candidate_highlight()
            self.shift_start_index = -1
