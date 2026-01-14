"""
主窗口模块
"""

import json
import sys
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QEvent, QObject, Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from ..ai.factory import generate_commit_message
from ..core.commit import execute_svn_commit
from ..core.parser import extract_path_from_display_text
from ..core.svn_executor import SVNCommandExecutor
from ..core.fs_helper import FileSystemHelper
from .constants import CHECKBOX_COLUMN, PATH_COLUMN
from .context_menu import ContextMenuBuilder
from .file_list_widget import FileListWidget
from .settings_dialog import SettingsDialog
from .styles import UIStyles
from .svn_loader import SVNStatusLoader


def _extract_status_from_display_text(display_text: str) -> str:
    """
    从显示文本中提取 SVN 状态码

    Args:
        display_text: 显示文本，格式如 "[M] file.cs"

    Returns:
        SVN 状态码（M/A/D/? 等）
    """
    if len(display_text) > 1 and display_text[0] == "[":
        return display_text[1]
    return ""


def check_pyqt5_available(items: Optional[List[Tuple[str, str]]]) -> bool:
    """
    检查 PyQt5 是否可用

    Args:
        items: 文件列表（用于错误消息）

    Returns:
        是否可用
    """
    try:
        from PyQt5.QtWidgets import QApplication

        return True
    except ImportError:
        print(
            json.dumps(
                {
                    "error": "PyQt5 not installed",
                    "message": "请运行: pip install PyQt5",
                    "available": [path for _, path in items or []],
                },
                ensure_ascii=False,
            )
        )
        return False


class TreeEventFilter(QObject):
    """树控件事件过滤器 - 处理路径点击和空白处清空备选项"""

    # 双击检测常量
    DOUBLE_CLICK_INTERVAL = 500  # ms
    DOUBLE_CLICK_THRESHOLD = 15  # px

    def __init__(
        self,
        tree_widget: QTreeWidget,
        file_list_widget: FileListWidget,
        svn_executor: SVNCommandExecutor,
        fs_helper: FileSystemHelper,
        refresh_callback=None,
    ):
        super().__init__()
        self.tree = tree_widget
        self.file_list = file_list_widget
        self._svn_executor = svn_executor
        self._fs_helper = fs_helper
        self._menu_builder = ContextMenuBuilder(
            svn_executor, fs_helper, tree_widget, refresh_callback
        )
        self._refresh_callback = refresh_callback

        # 双击检测
        self._last_click_time = 0
        self._last_click_pos = None

    def eventFilter(self, _obj, event):
        """处理鼠标点击和按键事件"""
        if event.type() == QEvent.MouseButtonPress:
            # 检测是否为双击（两次点击间隔小于500ms且位置相近）
            current_time = event.timestamp()
            if self._last_click_pos:
                pos_diff = (
                    abs(event.pos().x() - self._last_click_pos.x()) ** 2
                    + abs(event.pos().y() - self._last_click_pos.y()) ** 2
                ) ** 0.5
                if (
                    current_time - self._last_click_time < self.DOUBLE_CLICK_INTERVAL
                    and pos_diff < self.DOUBLE_CLICK_THRESHOLD
                ):
                    # 检测到双击，跳过处理，让itemDoubleClicked信号触发
                    return False

            self._last_click_time = current_time
            self._last_click_pos = event.pos()

            item = self.tree.itemAt(event.pos())
            if not item:
                # 点击空白处清空备选项
                self.file_list.clear_candidates()
            else:
                column = self.tree.columnAt(event.pos().x())
                if column == PATH_COLUMN:
                    return self._handle_path_column_click(item, event)
        elif event.type() == QEvent.KeyPress:
            return self._handle_key_press(event)
        return False

    def _handle_key_press(self, event):
        """处理按键事件 - F5 刷新"""
        if event.key() == Qt.Key_F5:
            if self._refresh_callback:
                self._refresh_callback()
            return True
        return False

    def _handle_path_column_click(self, item, event):
        """处理路径列点击（仅左键）"""
        if event.button() == Qt.LeftButton:
            index = self.tree.indexOfTopLevelItem(item)
            # Shift+点击只设置备选项，不改变复选框状态
            if QGuiApplication.keyboardModifiers() & Qt.ShiftModifier:
                self.file_list.handle_item_click(index, None, is_checkbox=False)
            else:
                # 普通点击切换复选框状态
                current_state = item.checkState(CHECKBOX_COLUMN)
                new_state = Qt.Unchecked if current_state == Qt.Checked else Qt.Checked
                self.file_list.handle_item_click(index, new_state, is_checkbox=False)
        return False


class MainWindow(QMainWindow):
    """SVN 提交助手主窗口"""

    # 窗口配置常量
    WINDOW_TITLE = "SVN 提交助手"
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    HELP_BUTTON_SIZE = 30
    CONFIRM_BUTTON_SHORTCUT = Qt.Key_Return | Qt.Key_Enter
    CANCEL_BUTTON_SHORTCUT = Qt.Key_Escape

    # 布局伸缩因子
    TOP_WIDGET_STRETCH = 3
    FILE_LIST_STRETCH = 7

    # 排序选项
    SORT_OPTIONS = ["默认顺序", "按路径", "按后缀", "按状态"]
    SORT_FIELDS = ["default", "path", "ext", "status"]

    def __init__(self, items: Optional[List[Tuple[str, str]]] = None):
        super().__init__()
        self._items = items
        self._original_items: List[Tuple[str, str]] = []
        self._items_for_display: List[Tuple[str, str]] = []
        self._result: Dict[str, Any] = {
            "selected": [],
            "commitMessage": "",
            "cancelled": False,
        }
        self._svn_loader: Optional[SVNStatusLoader] = None
        self._svn_executor = SVNCommandExecutor()
        self._fs_helper = FileSystemHelper()
        self._menu_builder = ContextMenuBuilder(
            self._svn_executor, self._fs_helper, self
        )

        # UI 组件（将在 _init_ui 中初始化）
        self.file_list: FileListWidget
        self.commit_message_input: QTextEdit
        self.generate_msg_btn: QPushButton
        self.confirm_btn: QPushButton
        self.cancel_btn: QPushButton
        self.status_label: QLabel
        self.search_input: QLineEdit
        self.sort_combo: QComboBox
        self.ascending_checkbox: QCheckBox

        # 初始化窗口
        self._init_window()
        self._init_ui()
        self._connect_signals()

        # 加载数据
        if items is not None:
            self._load_items(items)
        else:
            self._start_async_load()

    def _init_window(self) -> None:
        """初始化窗口基本属性"""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # 创建菜单栏
        menubar = self.menuBar()
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(lambda: SettingsDialog(self).exec_())
        menubar.addAction(settings_action)

    def _init_ui(self) -> None:
        """初始化 UI 布局"""
        # 中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建上部分控件和文件列表
        top_widget = self._create_top_widget()
        self.file_list = FileListWidget()

        # 创建垂直分割器
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(top_widget)
        splitter.addWidget(self.file_list.get_widget())
        splitter.setStretchFactor(0, self.TOP_WIDGET_STRETCH)
        splitter.setStretchFactor(1, self.FILE_LIST_STRETCH)

        layout.addWidget(splitter)

        # 添加按钮布局
        layout.addLayout(self._create_button_layout())

        # 添加状态栏和帮助按钮
        layout.addLayout(self._create_status_help_layout())

    def _create_top_widget(self) -> QWidget:
        """创建上部分控件（提交消息区域和搜索区域）"""
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # 提交消息输入框
        msg_label = QLabel("提交消息:")
        msg_label.setStyleSheet(UIStyles.BOLD_LABEL_STYLE)
        top_layout.addWidget(msg_label)

        self.commit_message_input = QTextEdit()
        self.commit_message_input.setPlaceholderText(
            '点击"AI 生成提交消息"自动生成，或手动输入...'
        )
        self.commit_message_input.setMinimumHeight(60)
        top_layout.addWidget(self.commit_message_input)

        # AI 生成按钮和提示
        ai_button_layout = QHBoxLayout()
        self.generate_msg_btn = QPushButton("AI 生成提交消息")
        self.generate_msg_btn.setStyleSheet(UIStyles.AI_BUTTON_STYLE)
        ai_hint = QLabel("(基于选中文件路径分析)")
        ai_hint.setStyleSheet(UIStyles.HINT_LABEL_STYLE)
        ai_button_layout.addWidget(self.generate_msg_btn)
        ai_button_layout.addWidget(ai_hint)
        ai_button_layout.addStretch()
        top_layout.addLayout(ai_button_layout)

        # 搜索框和排序控件
        search_sort_layout = QHBoxLayout()
        search_sort_layout.addWidget(self._create_search_container(), 2)
        search_sort_layout.addWidget(self._create_sort_container(), 1)
        top_layout.addLayout(search_sort_layout)

        return top_widget

    def _create_search_container(self) -> QWidget:
        """创建搜索框容器"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("搜索过滤:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "普通文本 / *.cs 通配符 （如 *.cs 匹配所有 .cs 文件）"
        )
        layout.addWidget(self.search_input)

        return container

    def _create_sort_container(self) -> QWidget:
        """创建排序控件容器"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("排序:"))

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(self.SORT_OPTIONS)
        self.sort_combo.setCurrentIndex(0)
        layout.addWidget(self.sort_combo)

        self.ascending_checkbox = QCheckBox("升序")
        self.ascending_checkbox.setChecked(True)
        layout.addWidget(self.ascending_checkbox)

        sort_btn = QPushButton("排序")
        sort_btn.setMaximumWidth(60)
        sort_btn.clicked.connect(self._on_sort)
        layout.addWidget(sort_btn)

        return container

    def _create_button_layout(self) -> QHBoxLayout:
        """创建按钮布局"""
        layout = QHBoxLayout()

        select_all_btn = QPushButton("全选")
        clear_btn = QPushButton("清空")
        invert_btn = QPushButton("反选")

        self.confirm_btn = QPushButton("确认 (Enter)")
        self.confirm_btn.setStyleSheet(UIStyles.CONFIRM_BUTTON_STYLE)

        self.cancel_btn = QPushButton("取消 (ESC)")
        self.cancel_btn.setStyleSheet(UIStyles.CANCEL_BUTTON_STYLE)

        layout.addWidget(select_all_btn)
        layout.addWidget(clear_btn)
        layout.addWidget(invert_btn)
        layout.addStretch()
        layout.addWidget(self.confirm_btn)
        layout.addWidget(self.cancel_btn)

        # 连接选择按钮信号
        select_all_btn.clicked.connect(self.file_list.select_all)
        clear_btn.clicked.connect(self.file_list.clear_selection)
        invert_btn.clicked.connect(self.file_list.invert_selection)

        return layout

    def _create_status_help_layout(self) -> QHBoxLayout:
        """创建状态栏和帮助按钮布局"""
        layout = QHBoxLayout()

        self.status_label = QLabel("正在加载...")
        self.status_label.setStyleSheet(UIStyles.STATUS_LABEL_STYLE)
        layout.addWidget(self.status_label)
        layout.addStretch()

        help_btn = QPushButton("?")
        help_btn.setFixedSize(self.HELP_BUTTON_SIZE, self.HELP_BUTTON_SIZE)
        help_btn.setToolTip("查看使用帮助")
        help_btn.clicked.connect(self._show_help_dialog)
        layout.addWidget(help_btn)

        return layout

    def _connect_signals(self) -> None:
        """连接信号和槽"""
        # 按钮信号
        self.confirm_btn.clicked.connect(self._on_confirm)
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.generate_msg_btn.clicked.connect(self._on_generate_message)

        # 搜索和排序信号
        self.search_input.textChanged.connect(self._on_search_changed)

        # 树控件信号
        self.file_list.tree.itemChanged.connect(self._on_tree_item_changed)

        # 禁用双击自动展开，启用自定义上下文菜单
        self.file_list.tree.setExpandsOnDoubleClick(False)
        self.file_list.tree.setContextMenuPolicy(Qt.CustomContextMenu)

        # 连接双击和右键菜单信号
        self.file_list.tree.itemDoubleClicked.connect(self._on_tree_double_click)
        self.file_list.tree.customContextMenuRequested.connect(
            self._on_tree_context_menu
        )

        # 安装事件过滤器
        event_filter = TreeEventFilter(
            self.file_list.tree,
            self.file_list,
            self._svn_executor,
            self._fs_helper,
            self._refresh_file_list,
        )
        self.file_list.tree.viewport().installEventFilter(event_filter)

        # 快捷键
        self.confirm_btn.setShortcut(self.CONFIRM_BUTTON_SHORTCUT)
        self.cancel_btn.setShortcut(self.CANCEL_BUTTON_SHORTCUT)

    def _load_items(self, items: List[Tuple[str, str]]) -> None:
        """加载文件列表数据"""
        self._original_items = list(items)
        self._items_for_display = list(items)

        for status, path in items:
            self.file_list.add_item(status, path)

        if len(items) == 0:
            self.status_label.setText("当前没有变更文件")
        else:
            self.status_label.setText(f"共 {len(items)} 个文件")

    def _start_async_load(self) -> None:
        """启动异步加载"""
        # 停止现有加载器
        if self._svn_loader is not None and self._svn_loader.isRunning():
            self._svn_loader.terminate()
            self._svn_loader.wait()

        # 创建并启动新加载器
        self._svn_loader = SVNStatusLoader()
        self._svn_loader.finished.connect(self._on_files_loaded)
        self._svn_loader.error.connect(self._on_load_error)
        self._svn_loader.start()

        self.status_label.setText("正在加载...")

    def _refresh_file_list(self) -> None:
        """刷新文件列表（使用异步加载）"""
        self._start_async_load()

    @pyqtSlot(list)
    def _on_files_loaded(self, files: List[Tuple[str, str]]) -> None:
        """文件列表加载完成槽函数"""
        self._original_items = list(files)
        self._items_for_display = list(files)

        # 保存当前选中状态
        checked_paths = set(self.file_list.get_checked_items())

        # 重建列表
        self.file_list.tree.clear()
        for status, path in files:
            self.file_list.add_item(status, path)
            # 恢复选中状态
            if path in checked_paths:
                last_item = self.file_list.tree.topLevelItem(
                    self.file_list.tree.topLevelItemCount() - 1
                )
                last_item.setCheckState(CHECKBOX_COLUMN, Qt.Checked)

        self.status_label.setText(f"共 {len(files)} 个文件")

    @pyqtSlot(str)
    def _on_load_error(self, error_msg: str) -> None:
        """加载错误槽函数"""
        self.status_label.setText(f"加载失败: {error_msg}")
        QMessageBox.warning(self, "加载失败", error_msg)

    def _on_confirm(self) -> None:
        """确认提交"""
        selected_files = self.file_list.get_checked_items()

        if not selected_files:
            QMessageBox.warning(self, "提示", "请选择要提交的文件")
            return

        commit_message = self.commit_message_input.toPlainText().strip()

        if not commit_message:
            QMessageBox.warning(self, "提示", "请输入提交消息")
            return

        # 禁用按钮防止重复提交
        self.confirm_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.confirm_btn.setText("正在提交...")

        # 强制刷新 UI
        QApplication.processEvents()

        # 执行 SVN 提交
        commit_result = execute_svn_commit(selected_files, commit_message)

        if commit_result["success"]:
            # 成功：更新状态栏，立即关闭
            revision = commit_result.get("revision", "未知")
            self.status_label.setText(f"✓ 提交成功 (r{revision})")
            self._result["selected"] = selected_files
            self._result["commitMessage"] = commit_message
            self._result["cancelled"] = False
            self._result["commitResult"] = {
                "success": True,
                "revision": revision,
                "message": "提交成功",
            }
            self.close()
        else:
            # 失败：弹出错误对话框，恢复按钮
            error_msg = commit_result.get("output", "未知错误")
            QMessageBox.critical(self, "提交失败", error_msg)

            # 恢复按钮状态
            self.confirm_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
            self.confirm_btn.setText("确认 (Enter)")

            # 更新结果
            self._result["selected"] = selected_files
            self._result["commitMessage"] = commit_message
            self._result["cancelled"] = False
            self._result["commitResult"] = {
                "success": False,
                "revision": None,
                "message": "提交失败",
            }

    def _on_cancel(self) -> None:
        """取消操作"""
        self._result["selected"] = []
        self._result["commitMessage"] = ""
        self._result["cancelled"] = True
        self.close()

    def _on_generate_message(self) -> None:
        """生成提交消息"""
        selected_files = self.file_list.get_checked_items()
        if selected_files:
            # 显示加载提示
            self.commit_message_input.setPlainText(
                "正在调用 AI 生成提交消息...\n\n请稍候..."
            )
            self.generate_msg_btn.setEnabled(False)

            # 强制刷新 UI
            QApplication.processEvents()

            # 调用生成函数
            commit_message = generate_commit_message(selected_files)

            # 填入输入框
            self.commit_message_input.setPlainText(commit_message)
            self.generate_msg_btn.setEnabled(True)
        else:
            self.commit_message_input.setPlainText("chore: 提交变更")

    def _on_search_changed(self, text: str) -> None:
        """搜索文本变化处理"""
        self.file_list.filter_by_text(text, self._original_items)
        if text:
            self.status_label.setText(
                f"过滤: {self.file_list.count()} / {len(self._original_items)}"
            )
        else:
            self.status_label.setText(f"共 {len(self._original_items)} 个文件")

    def _on_sort(self) -> None:
        """执行排序"""
        sort_index = self.sort_combo.currentIndex()
        ascending = self.ascending_checkbox.isChecked()

        sort_by = self.SORT_FIELDS[sort_index] if sort_index > 0 else None

        if sort_by:
            self.file_list.sort_items(sort_by, ascending)
        else:
            # 恢复默认顺序
            checked_paths = set(self.file_list.get_checked_items())
            self.file_list.tree.clear()
            for status, path in self._original_items:
                self.file_list.add_item(status, path)
                if path in checked_paths:
                    last_item = self.file_list.tree.topLevelItem(
                        self.file_list.tree.topLevelItemCount() - 1
                    )
                    last_item.setCheckState(CHECKBOX_COLUMN, Qt.Checked)

    def _on_tree_item_changed(self, item, column: int) -> None:
        """树控件项改变事件"""
        if column == CHECKBOX_COLUMN:
            index = self.file_list.tree.indexOfTopLevelItem(item)
            new_state = item.checkState(CHECKBOX_COLUMN)
            self.file_list.handle_item_click(index, new_state)

    def _on_tree_double_click(self, item, column: int) -> None:
        """处理双击事件 - 打开 SVN diff"""
        if item and column == PATH_COLUMN:
            file_path = extract_path_from_display_text(item.text(PATH_COLUMN))
            if file_path:
                self._svn_executor.diff(file_path)

    def _on_tree_context_menu(self, pos) -> None:
        """显示右键菜单"""
        item = self.file_list.tree.itemAt(pos)

        # 如果 itemAt 返回 None，可能是：
        # 1. 点击空白处 → 不显示菜单
        # 2. 键盘触发（pos 为无效坐标）→ 使用 currentItem
        if not item:
            if pos.x() == 0 and pos.y() == 0:
                item = self.file_list.tree.currentItem()
            else:
                return

        if item:
            file_path = extract_path_from_display_text(item.text(PATH_COLUMN))
            if file_path:
                status = _extract_status_from_display_text(item.text(PATH_COLUMN))
                menu = self._menu_builder.build_menu(
                    file_path, status, self.file_list.tree
                )
                menu.exec_(self.file_list.tree.viewport().mapToGlobal(pos))

    def _show_help_dialog(self) -> None:
        """显示帮助对话框"""
        help_text = """<h3>SVN 提交助手 - 使用帮助</h3>

<h4>文件选择</h4>
<ul>
    <li><b>复选框点击</b>：确认选择/取消文件</li>
    <li><b>路径点击</b>：高亮选中文件（蓝色背景），点击复选框确认</li>
    <li><b>Shift + 路径点击</b>：范围选择（两次点击确定范围）</li>
</ul>

<h4>搜索过滤</h4>
<ul>
    <li><b>普通文本</b>：大小写不敏感的包含匹配</li>
    <li><b>通配符</b>：*.cs 匹配所有 .cs 文件，Test*.cs 匹配以 Test 开头的 .cs 文件</li>
</ul>

<h4>排序功能</h4>
<ul>
    <li><b>按路径</b>：按文件路径字母顺序排序</li>
    <li><b>按后缀</b>：按文件扩展名分组排序（无后缀排在最后）</li>
    <li><b>按状态</b>：按 SVN 状态码（M/A/D/?）排序</li>
    <li><b>升序/降序</b>：勾选"升序"切换排序方向</li>
</ul>

<h4>快捷操作</h4>
<ul>
    <li><b>F5</b>：刷新 SVN 状态（重新加载文件列表）</li>
    <li><b>双击路径</b>：打开 SVN diff 对比工具</li>
    <li><b>右键路径</b>：显示 SVN 操作菜单（查看差异/日志/注释、还原、添加、删除等）</li>
    <li><b>Enter</b>：确认提交</li>
    <li><b>ESC</b>：取消</li>
</ul>

<h4>状态颜色</h4>
<ul>
    <li><span style="color:#2196F3">[M]</span> 修改</li>
    <li><span style="color:#000000">[A]</span> 新增</li>
    <li><span style="color:#F44336">[D]</span> 删除</li>
    <li><span style="color:#000000">[?]</span> 未跟踪</li>
</ul>"""

        dialog = QDialog(self)
        dialog.setWindowTitle("使用帮助")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        help_label = QLabel(help_text)
        help_label.setTextFormat(Qt.RichText)
        help_label.setWordWrap(True)
        help_label.setOpenExternalLinks(False)
        layout.addWidget(help_label)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        dialog.exec_()

    def closeEvent(self, event) -> None:
        """窗口关闭事件 - 清理资源"""
        if self._svn_loader is not None and self._svn_loader.isRunning():
            self._svn_loader.terminate()
            self._svn_loader.wait()
        event.accept()

    def get_result(self) -> Dict[str, Any]:
        """获取操作结果"""
        return self._result


def show_quick_pick(items: Optional[List[Tuple[str, str]]] = None) -> Dict[str, Any]:
    """
    使用 PyQt5 显示 QuickPick 界面。

    Args:
        items: (状态, 文件路径) 元组列表，如果为 None 则异步加载

    Returns:
        包含 selected、commitMessage、cancelled、commitResult 的字典
    """
    if not check_pyqt5_available(items):
        sys.exit(1)

    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("SVN 提交助手")

    # 创建并显示主窗口
    window = MainWindow(items)
    window.show()

    # 如果没有提供 items，延迟启动异步加载
    if items is None:
        QTimer.singleShot(0, window._start_async_load)

    app.exec_()

    return window.get_result()
