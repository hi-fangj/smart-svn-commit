"""
右键菜单常量定义
"""

from PyQt5.QtWidgets import QStyle


class MenuAction:
    """菜单操作标识"""

    DIFF = "diff"
    LOG = "log"
    BLAME = "blame"
    REVERT = "revert"
    ADD = "add"
    DELETE = "delete"
    DELETE_FILE = "delete_file"
    OPEN_FILE = "open_file"
    OPEN_FOLDER = "open_folder"


# 状态对应的菜单操作配置
STATUS_MENU_ACTIONS = {
    "M": [MenuAction.DIFF, MenuAction.LOG, MenuAction.BLAME, MenuAction.REVERT, MenuAction.DELETE],
    "A": [MenuAction.DIFF, MenuAction.LOG, MenuAction.BLAME, MenuAction.DELETE],
    "?": [
        MenuAction.DIFF,
        MenuAction.LOG,
        MenuAction.BLAME,
        MenuAction.ADD,
        MenuAction.DELETE_FILE,
    ],
    "R": [MenuAction.DIFF, MenuAction.LOG, MenuAction.BLAME, MenuAction.DELETE],
    "~": [MenuAction.DIFF, MenuAction.LOG, MenuAction.BLAME, MenuAction.DELETE],
}

# 通用菜单操作（所有状态都显示）
COMMON_MENU_ACTIONS = [MenuAction.DIFF, MenuAction.LOG, MenuAction.BLAME]

# 文件操作菜单
FILE_MENU_ACTIONS = [MenuAction.OPEN_FILE, MenuAction.OPEN_FOLDER]

# 菜单操作显示名称
MENU_ACTION_LABELS = {
    MenuAction.DIFF: "查看差异",
    MenuAction.LOG: "查看日志",
    MenuAction.BLAME: "查看注释 (Blame)",
    MenuAction.REVERT: "还原",
    MenuAction.ADD: "添加",
    MenuAction.DELETE: "删除",
    MenuAction.DELETE_FILE: "删除",
    MenuAction.OPEN_FILE: "打开文件",
    MenuAction.OPEN_FOLDER: "打开所在目录",
}

# 菜单操作对应的标准图标 (使用 QStyle 标准像素图)
MENU_ACTION_ICONS = {
    MenuAction.DIFF: QStyle.SP_FileIcon,
    MenuAction.LOG: QStyle.SP_FileDialogDetailedView,
    MenuAction.BLAME: QStyle.SP_FileDialogContentsView,
    MenuAction.REVERT: QStyle.SP_BrowserReload,
    MenuAction.ADD: QStyle.SP_DialogApplyButton,
    MenuAction.DELETE: QStyle.SP_TrashIcon,
    MenuAction.DELETE_FILE: QStyle.SP_DialogCancelButton,
    MenuAction.OPEN_FILE: QStyle.SP_FileIcon,
    MenuAction.OPEN_FOLDER: QStyle.SP_DirOpenIcon,
}
