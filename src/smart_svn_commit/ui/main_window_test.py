"""
主窗口模块
"""

import json
import subprocess
import sys
from typing import List, Tuple, Dict, Any

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTreeWidget,
    QMenu,
    QAction,
    QTextEdit,
    QMessageBox,
    QSplitter,
    QComboBox,
    QCheckBox,
    QDialog,
)
from PyQt5.QtCore import Qt, QEvent, QObject

from .constants import CHECKBOX_COLUMN, PATH_COLUMN, STATUS_PREFIX_SEPARATOR
from .styles import UIStyles
from .file_list_widget import FileListWidget
from .context_menu import ContextMenuBuilder
from .commit_message import get_file_diff, generate_commit_message_with_ai
from ..core.parser import parse_svn_status
from ..core.commit import execute_svn_commit
from ..core.config import load_config
from ..core.svn_executor import SVNCommandExecutor
from ..core.fs_helper import FileSystemHelper
from ..utils.filters import apply_ignore_patterns
