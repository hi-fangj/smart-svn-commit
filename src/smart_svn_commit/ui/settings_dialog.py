"""
设置对话框模块
"""

from typing import Any, Dict, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QDialog,
    QTabWidget,
    QWidget,
)

from ..core.config import get_default_config, load_config, save_config


class SettingsDialog(QDialog):
    """设置对话框 - 使用标签页组织设置分类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self._config = load_config()
        self._init_ui()
        self._load_current_config()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 创建标签页控件
        tab_widget = QTabWidget()

        # AI 配置标签页
        ai_tab = self._create_ai_config_tab()
        tab_widget.addTab(ai_tab, "AI 配置")

        # 界面设置标签页（占位）
        ui_tab = self._create_placeholder_tab("界面设置", "未来可添加：主题、字体、界面布局等设置")
        tab_widget.addTab(ui_tab, "界面设置")

        # 提交设置标签页（占位）
        commit_tab = self._create_placeholder_tab("提交设置", "未来可添加：提交类型、范围列表、忽略规则等设置")
        tab_widget.addTab(commit_tab, "提交设置")

        # 默认显示第一个标签页（AI 配置）
        tab_widget.setCurrentIndex(0)

        layout.addWidget(tab_widget)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        restore_btn = QPushButton("恢复默认")
        restore_btn.clicked.connect(self._restore_defaults)
        button_layout.addWidget(restore_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def _create_ai_config_tab(self) -> QWidget:
        """创建 AI 配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # AI 配置组
        ai_group = QGroupBox("AI API 配置")
        ai_layout = QFormLayout()

        # 启用 AI
        self._enabled_checkbox = QCheckBox("启用 AI 生成提交消息")
        ai_layout.addRow(self._enabled_checkbox)

        # Base URL
        self._base_url_input = QLineEdit()
        self._base_url_input.setPlaceholderText("https://api.openai.com/v1")
        ai_layout.addRow("Base URL:", self._base_url_input)

        # API Key
        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.Password)
        self._api_key_input.setPlaceholderText("sk-...")
        ai_layout.addRow("API Key:", self._api_key_input)

        # 模型名称
        self._model_input = QLineEdit()
        self._model_input.setPlaceholderText("gpt-3.5-turbo")
        ai_layout.addRow("模型名称:", self._model_input)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # 提示词配置组
        prompts_group = QGroupBox("提示词配置")
        prompts_layout = QFormLayout()

        # 系统提示词
        self._system_prompt_input = QTextEdit()
        self._system_prompt_input.setMinimumHeight(100)
        self._system_prompt_input.setMaximumHeight(150)
        prompts_layout.addRow("系统提示词:", self._system_prompt_input)

        # 用户提示词模板
        self._user_prompt_input = QTextEdit()
        self._user_prompt_input.setMinimumHeight(80)
        self._user_prompt_input.setMaximumHeight(120)
        self._user_prompt_input.setPlaceholderText('使用 {diff_summary} 作为占位符')
        prompts_layout.addRow("用户提示词模板:", self._user_prompt_input)

        prompts_group.setLayout(prompts_layout)
        layout.addWidget(prompts_group)

        layout.addStretch()
        return tab

    def _create_placeholder_tab(self, title: str, description: str) -> QWidget:
        """创建占位标签页（用于未来扩展）"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 占位提示
        placeholder_label = QLabel(f"{title}\n\n{description}")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("color: #888888; font-size: 14px;")
        layout.addWidget(placeholder_label)

        layout.addStretch()
        return tab

    def _load_ai_config_to_form(self, ai_config: Dict[str, Any]) -> None:
        """加载 AI 配置到表单"""
        self._enabled_checkbox.setChecked(ai_config.get("enabled", False))
        self._base_url_input.setText(ai_config.get("baseUrl", ""))
        self._api_key_input.setText(ai_config.get("apiKey", ""))
        self._model_input.setText(ai_config.get("model", ""))

        prompts = ai_config.get("prompts", {})
        self._system_prompt_input.setPlainText(prompts.get("system", ""))
        self._user_prompt_input.setPlainText(prompts.get("user", ""))

    def _load_current_config(self):
        """加载当前配置到表单"""
        ai_config = self._config.get("aiApi", {})
        self._load_ai_config_to_form(ai_config)

    def _restore_defaults(self):
        """恢复默认配置"""
        default_config = get_default_config()
        ai_config = default_config.get("aiApi", {})
        self._load_ai_config_to_form(ai_config)

    def _validate_config(self) -> Tuple[bool, str]:
        """验证配置"""
        if not self._enabled_checkbox.isChecked():
            return True, ""

        base_url = self._base_url_input.text().strip()
        api_key = self._api_key_input.text().strip()

        if not base_url:
            return False, "启用 AI 时，Base URL 不能为空"

        if not api_key:
            return False, "启用 AI 时，API Key 不能为空"

        if not base_url.startswith(("http://", "https://")):
            return False, "Base URL 必须以 http:// 或 https:// 开头"

        return True, ""

    def _build_ai_config(self) -> Dict[str, Any]:
        """从表单构建 AI 配置"""
        return {
            "enabled": self._enabled_checkbox.isChecked(),
            "baseUrl": self._base_url_input.text().strip(),
            "apiKey": self._api_key_input.text().strip(),
            "model": self._model_input.text().strip() or "gpt-3.5-turbo",
            "prompts": {
                "system": self._system_prompt_input.toPlainText().strip(),
                "user": self._user_prompt_input.toPlainText().strip(),
            },
        }

    def _save_config(self):
        """保存配置"""
        is_valid, error_msg = self._validate_config()
        if not is_valid:
            QMessageBox.warning(self, "配置验证失败", error_msg)
            return

        self._config["aiApi"] = self._build_ai_config()

        if save_config(self._config):
            QMessageBox.information(self, "保存成功", "配置已保存")
            self.accept()
        else:
            QMessageBox.critical(self, "保存失败", "无法保存配置文件")
