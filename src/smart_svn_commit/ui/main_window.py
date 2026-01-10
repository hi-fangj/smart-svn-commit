"""
主窗口模块
"""

import json
import sys
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QEvent, QObject, Qt, pyqtSlot
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
from ..core.parser import extract_path_from_display_text, parse_svn_status
from ..core.svn_executor import SVNCommandExecutor
from ..core.fs_helper import FileSystemHelper
from .constants import CHECKBOX_COLUMN, PATH_COLUMN
from .context_menu import ContextMenuBuilder
from .file_list_widget import FileListWidget
from .settings_dialog import SettingsDialog
from .styles import UIStyles
from .svn_loader import SVNStatusLoader


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


def show_quick_pick(items: Optional[List[Tuple[str, str]]] = None) -> Dict[str, Any]:
    """
    使用 PyQt5 显示 QuickPick 界面。

    Args:
        items: (状态, 文件路径) 元组列表，如果为 None 则异步加载

    Returns:
        包含 selected、commitMessage、cancelled、commitResult 的字典

    Note:
        此函数较长，未来可考虑拆分为专门的 UI 构建类
    """
    if not check_pyqt5_available(items):
        sys.exit(1)

    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("SVN 提交助手")

    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("SVN 提交助手")
    window.resize(900, 600)

    # 创建菜单栏
    menubar = window.menuBar()
    settings_menu = menubar.addMenu("设置")

    # 设置菜单项
    settings_action = QAction("设置", window)
    settings_action.triggered.connect(lambda: SettingsDialog(window).exec_())
    settings_menu.addAction(settings_action)

    # 中心部件
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # 主布局
    layout = QVBoxLayout(central_widget)

    # 创建上部分控件容器（包含提交消息区域和搜索区域）
    top_widget = QWidget()
    top_layout = QVBoxLayout(top_widget)
    top_layout.setContentsMargins(0, 0, 0, 0)

    # 提交消息输入框（放在文件选择上面）
    msg_label = QLabel("提交消息:")
    msg_label.setStyleSheet(UIStyles.BOLD_LABEL_STYLE)
    top_layout.addWidget(msg_label)

    commit_message_input = QTextEdit()
    commit_message_input.setPlaceholderText('点击"AI 生成提交消息"自动生成，或手动输入...')
    commit_message_input.setMinimumHeight(60)
    top_layout.addWidget(commit_message_input)

    # AI 生成按钮和提示
    ai_button_layout = QHBoxLayout()
    generate_msg_btn = QPushButton("AI 生成提交消息")
    generate_msg_btn.setStyleSheet(UIStyles.AI_BUTTON_STYLE)
    ai_hint = QLabel("(基于选中文件路径分析)")
    ai_hint.setStyleSheet(UIStyles.HINT_LABEL_STYLE)
    ai_button_layout.addWidget(generate_msg_btn)
    ai_button_layout.addWidget(ai_hint)
    ai_button_layout.addStretch()
    top_layout.addLayout(ai_button_layout)

    # 搜索框和排序控件
    search_sort_layout = QHBoxLayout()

    # 左侧：搜索框
    search_container = QWidget()
    search_container_layout = QHBoxLayout(search_container)
    search_container_layout.setContentsMargins(0, 0, 0, 0)
    search_container_layout.addWidget(QLabel("搜索过滤:"))
    search_input = QLineEdit()
    search_input.setPlaceholderText("普通文本 / *.cs 通配符 （如 *.cs 匹配所有 .cs 文件）")
    search_container_layout.addWidget(search_input)
    search_sort_layout.addWidget(search_container, 2)

    # 右侧：排序控件
    sort_container = QWidget()
    sort_container_layout = QHBoxLayout(sort_container)
    sort_container_layout.setContentsMargins(0, 0, 0, 0)
    sort_container_layout.addWidget(QLabel("排序:"))

    sort_combo = QComboBox()
    sort_combo.addItems(["默认顺序", "按路径", "按后缀", "按状态"])
    sort_combo.setCurrentIndex(0)
    sort_container_layout.addWidget(sort_combo)

    ascending_checkbox = QCheckBox("升序")
    ascending_checkbox.setChecked(True)
    sort_container_layout.addWidget(ascending_checkbox)

    sort_sort_btn = QPushButton("排序")
    sort_sort_btn.setMaximumWidth(60)
    sort_container_layout.addWidget(sort_sort_btn)

    search_sort_layout.addWidget(sort_container, 1)
    top_layout.addLayout(search_sort_layout)

    # 文件列表（使用自定义控件）
    file_list = FileListWidget()

    # 保存原始数据（用于过滤和刷新）
    original_items: List[Tuple[str, str]] = []
    items_for_display: List[Tuple[str, str]] = []

    # 如果提供了 items，直接使用；否则异步加载
    if items is not None:
        original_items = list(items)
        items_for_display = list(items)

    # 填充列表数据（如果有）
    for status, path in items_for_display:
        file_list.add_item(status, path)

    # 创建垂直分割器，实现动态高度调整
    splitter = QSplitter(Qt.Vertical)
    splitter.addWidget(top_widget)
    splitter.addWidget(file_list.get_widget())

    # 设置伸缩因子
    splitter.setStretchFactor(0, 3)
    splitter.setStretchFactor(1, 7)

    # 将分割器添加到主布局
    layout.addWidget(splitter)

    # 按钮布局
    button_layout = QHBoxLayout()

    select_all_btn = QPushButton("全选")
    clear_btn = QPushButton("清空")
    invert_btn = QPushButton("反选")

    confirm_btn = QPushButton("确认 (Enter)")
    confirm_btn.setStyleSheet(UIStyles.CONFIRM_BUTTON_STYLE)

    cancel_btn = QPushButton("取消 (ESC)")
    cancel_btn.setStyleSheet(UIStyles.CANCEL_BUTTON_STYLE)

    button_layout.addWidget(select_all_btn)
    button_layout.addWidget(clear_btn)
    button_layout.addWidget(invert_btn)
    button_layout.addStretch()
    button_layout.addWidget(confirm_btn)
    button_layout.addWidget(cancel_btn)

    layout.addLayout(button_layout)

    # 状态栏和帮助按钮
    status_help_layout = QHBoxLayout()

    # 初始状态文本：如果有 items 显示数量，否则显示加载中
    if items is not None:
        if len(items) == 0:
            status_label = QLabel("当前没有变更文件")
        else:
            status_label = QLabel(f"共 {len(items)} 个文件")
    else:
        status_label = QLabel("正在加载...")

    status_label.setStyleSheet(UIStyles.STATUS_LABEL_STYLE)
    status_help_layout.addWidget(status_label)
    status_help_layout.addStretch()

    help_btn = QPushButton("?")
    help_btn.setFixedSize(30, 30)
    help_btn.setToolTip("查看使用帮助")
    status_help_layout.addWidget(help_btn)

    layout.addLayout(status_help_layout)

    # 保存结果
    result = {"selected": [], "commitMessage": "", "cancelled": False}

    # 连接信号和槽
    def on_confirm():
        selected_files = file_list.get_checked_items()

        if not selected_files:
            QMessageBox.warning(window, "提示", "请选择要提交的文件")
            return

        commit_message = commit_message_input.toPlainText().strip()

        if not commit_message:
            QMessageBox.warning(window, "提示", "请输入提交消息")
            return

        # 禁用按钮防止重复提交
        confirm_btn.setEnabled(False)
        cancel_btn.setEnabled(False)
        confirm_btn.setText("正在提交...")

        # 强制刷新 UI
        QApplication.processEvents()

        # 执行 SVN 提交
        commit_result = execute_svn_commit(selected_files, commit_message)

        if commit_result["success"]:
            # 成功：更新状态栏，立即关闭
            revision = commit_result.get("revision", "未知")
            status_label.setText(f"✓ 提交成功 (r{revision})")
            result["selected"] = selected_files
            result["commitMessage"] = commit_message
            result["cancelled"] = False
            result["commitResult"] = {"success": True, "revision": revision, "message": "提交成功"}
            window.close()
        else:
            # 失败：弹出错误对话框，恢复按钮
            error_msg = commit_result.get("output", "未知错误")
            QMessageBox.critical(window, "提交失败", error_msg)

            # 恢复按钮状态，允许重试
            confirm_btn.setEnabled(True)
            cancel_btn.setEnabled(True)
            confirm_btn.setText("确认 (Enter)")

            # 更新结果但保持窗口打开
            result["selected"] = selected_files
            result["commitMessage"] = commit_message
            result["cancelled"] = False
            result["commitResult"] = {"success": False, "revision": None, "message": "提交失败"}

    def on_cancel():
        result["selected"] = []
        result["commitMessage"] = ""
        result["cancelled"] = True
        window.close()

    def on_generate_message():
        """生成提交消息"""
        selected_files = file_list.get_checked_items()
        if selected_files:
            # 显示加载提示
            commit_message_input.setPlainText("正在调用 AI 生成提交消息...\n\n请稍候...")
            generate_msg_btn.setEnabled(False)

            # 强制刷新 UI
            QApplication.processEvents()

            # 调用统一的生成函数
            commit_message = generate_commit_message(selected_files)

            # 将生成的消息填入输入框
            commit_message_input.setPlainText(commit_message)
            generate_msg_btn.setEnabled(True)
        else:
            commit_message_input.setPlainText("chore: 提交变更")

    def on_search_changed(text):
        file_list.filter_by_text(text, original_items)
        if text:
            status_label.setText(f"过滤: {file_list.count()} / {len(original_items)}")
        else:
            status_label.setText(f"共 {len(original_items)} 个文件")

    def on_select_all():
        file_list.select_all()

    def on_clear():
        file_list.clear_selection()

    def on_invert():
        file_list.invert_selection()

    def on_sort():
        """执行排序"""
        sort_index = sort_combo.currentIndex()
        ascending = ascending_checkbox.isChecked()

        # 映射索引到排序字段
        sort_fields = ["default", "path", "ext", "status"]
        sort_by = sort_fields[sort_index] if sort_index > 0 else None

        if sort_by:
            file_list.sort_items(sort_by, ascending)
        else:
            # 恢复默认顺序（使用原始数据）
            checked_paths = set(file_list.get_checked_items())
            file_list.tree.clear()
            for status, path in original_items:
                file_list.add_item(status, path)
                if path in checked_paths:
                    last_item = file_list.tree.topLevelItem(
                        file_list.tree.topLevelItemCount() - 1
                    )
                    last_item.setCheckState(CHECKBOX_COLUMN, Qt.Checked)

    # 异步加载器（初始为 None，需要时创建）
    svn_loader: Optional[SVNStatusLoader] = None

    @pyqtSlot(list)
    def on_files_loaded(files: List[Tuple[str, str]]) -> None:
        """文件列表加载完成槽函数"""
        nonlocal original_items, items_for_display

        # 更新数据
        original_items = list(files)
        items_for_display = list(files)

        # 保存当前选中状态
        checked_paths = set(file_list.get_checked_items())

        # 重建列表
        file_list.tree.clear()
        for status, path in files:
            file_list.add_item(status, path)
            # 恢复选中状态（如果文件仍在列表中）
            if path in checked_paths:
                last_item = file_list.tree.topLevelItem(
                    file_list.tree.topLevelItemCount() - 1
                )
                last_item.setCheckState(CHECKBOX_COLUMN, Qt.Checked)

        # 更新状态栏
        status_label.setText(f"共 {len(files)} 个文件")

    @pyqtSlot(str)
    def on_load_error(error_msg: str) -> None:
        """加载错误槽函数"""
        status_label.setText(f"加载失败: {error_msg}")
        QMessageBox.warning(window, "加载失败", error_msg)

    def start_async_load() -> None:
        """启动异步加载"""
        nonlocal svn_loader

        # 如果已有加载器在运行，先停止
        if svn_loader is not None and svn_loader.isRunning():
            svn_loader.terminate()
            svn_loader.wait()

        # 创建并启动新加载器
        svn_loader = SVNStatusLoader()
        svn_loader.finished.connect(on_files_loaded)
        svn_loader.error.connect(on_load_error)
        svn_loader.start()

        # 更新状态
        status_label.setText("正在加载...")

    def refresh_file_list():
        """刷新文件列表（使用异步加载）"""
        start_async_load()

    def show_help_dialog():
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

        dialog = QDialog(window)
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

    # 处理树形控件项改变事件（复选框状态改变时触发）
    def on_tree_item_changed(item, column):
        """只处理复选框列"""
        if column == CHECKBOX_COLUMN:
            index = file_list.tree.indexOfTopLevelItem(item)
            new_state = item.checkState(CHECKBOX_COLUMN)
            file_list.handle_item_click(index, new_state)

    # 安装事件过滤器（用于路径点击和空白处清空备选项）
    class TreeEventFilter(QObject):
        """树控件事件过滤器 - 简化版，委托给专门的类处理操作"""

        def __init__(
            self,
            tree_widget: QTreeWidget,
            file_list_widget: "FileListWidget",
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

        def eventFilter(self, _obj, event):
            """处理鼠标点击事件"""
            if event.type() == QEvent.MouseButtonPress:
                item = self.tree.itemAt(event.pos())
                if not item:
                    # 点击空白处清空备选项
                    self.file_list.clear_candidates()
                else:
                    column = self.tree.columnAt(event.pos().x())
                    if column == PATH_COLUMN:
                        return self._handle_path_column_click(item, event)
            elif event.type() == QEvent.MouseButtonDblClick:
                return self._handle_double_click(event)
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
            """处理路径列点击"""
            if event.button() == Qt.RightButton:
                # 右键显示菜单
                file_path = extract_path_from_display_text(item.text(PATH_COLUMN))
                if file_path:
                    status = self._extract_status(item.text(PATH_COLUMN))
                    menu = self._menu_builder.build_menu(file_path, status, self.tree)
                    menu.exec_(event.globalPos())
                return True
            else:
                # 左键切换复选框
                index = self.tree.indexOfTopLevelItem(item)
                current_state = item.checkState(CHECKBOX_COLUMN)
                new_state = Qt.Unchecked if current_state == Qt.Checked else Qt.Checked
                self.file_list.handle_item_click(index, new_state, is_checkbox=False)
            return False

        def _handle_double_click(self, event):
            """处理双击事件 - 打开 SVN diff"""
            item = self.tree.itemAt(event.pos())
            if item:
                column = self.tree.columnAt(event.pos().x())
                if column == PATH_COLUMN:
                    file_path = extract_path_from_display_text(item.text(PATH_COLUMN))
                    if file_path:
                        self._svn_executor.diff(file_path)
            return False

        @staticmethod
        def _extract_status(display_text: str) -> str:
            """从显示文本中提取状态码"""
            if len(display_text) > 1 and display_text[0] == "[":
                return display_text[1]
            return ""

    # 创建辅助实例
    svn_executor = SVNCommandExecutor()
    fs_helper = FileSystemHelper()
    event_filter = TreeEventFilter(
        file_list.tree, file_list, svn_executor, fs_helper, refresh_file_list
    )
    file_list.tree.viewport().installEventFilter(event_filter)

    # 连接按钮和事件
    confirm_btn.clicked.connect(on_confirm)
    cancel_btn.clicked.connect(on_cancel)
    select_all_btn.clicked.connect(on_select_all)
    clear_btn.clicked.connect(on_clear)
    invert_btn.clicked.connect(on_invert)
    generate_msg_btn.clicked.connect(on_generate_message)
    search_input.textChanged.connect(on_search_changed)
    sort_sort_btn.clicked.connect(on_sort)
    help_btn.clicked.connect(show_help_dialog)

    # 只连接 itemChanged 事件（复选框状态改变）
    file_list.tree.itemChanged.connect(on_tree_item_changed)

    # 支持快捷键
    confirm_btn.setShortcut(Qt.Key_Return | Qt.Key_Enter)
    cancel_btn.setShortcut(Qt.Key_Escape)

    # 显示窗口
    window.show()

    # 如果没有提供 items，启动异步加载
    if items is None:
        # 使用 QTimer 延迟启动，确保 UI 先显示
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, start_async_load)

    app.exec_()

    return result
