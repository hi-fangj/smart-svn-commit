"""
Windows 右键菜单安装模块
"""

import os
import sys
from pathlib import Path

# 确保只有在 Windows 上才导入
if sys.platform == "win32":
    import winreg

from .registry import (
    delete_registry_key,
    registry_key_exists,
    set_registry_value,
)

# 右键菜单注册表路径
# 文件夹背景右键菜单
CONTEXT_MENU_BG_KEY_PATH = (
    r"Software\Classes\Directory\Background\shell\smart-svn-commit"
)
CONTEXT_MENU_BG_COMMAND_KEY_PATH = f"{CONTEXT_MENU_BG_KEY_PATH}\\command"
# 文件夹右键菜单
CONTEXT_MENU_DIR_KEY_PATH = r"Software\Classes\Directory\shell\smart-svn-commit"
CONTEXT_MENU_DIR_COMMAND_KEY_PATH = f"{CONTEXT_MENU_DIR_KEY_PATH}\\command"
# 兼容旧版本的常量
CONTEXT_MENU_KEY_PATH = CONTEXT_MENU_BG_KEY_PATH
CONTEXT_MENU_COMMAND_KEY_PATH = CONTEXT_MENU_BG_COMMAND_KEY_PATH


def is_svn_working_copy(path: str) -> bool:
    """
    检查目录是否是 SVN 工作副本

    Args:
        path: 目录路径

    Returns:
        是否是 SVN 工作副本
    """
    return (Path(path) / ".svn").is_dir()


def handle_context_menu(path: str) -> None:
    """
    处理右键菜单调用（从注册表命令调用）

    Args:
        path: 用户右键点击的目录路径
    """
    # 检查是否是 SVN 工作副本
    if not is_svn_working_copy(path):
        # 不是 SVN 目录，静默退出
        sys.exit(0)

    # 是 SVN 目录，启动 GUI
    try:
        # 获取当前脚本所在目录的安装路径
        install_dir = Path(__file__).parent.parent.parent.parent
        if (install_dir / "smart_svn_commit").exists():
            src_dir = install_dir / "src"
            sys.path.insert(0, str(src_dir))

        from smart_svn_commit.core.commit import run_svn_status
        from smart_svn_commit.core.config import load_config
        from smart_svn_commit.core.parser import parse_svn_status
        from smart_svn_commit.ui.main_window import show_quick_pick
        from smart_svn_commit.utils.filters import apply_ignore_patterns

        # 切换到目标目录
        os.chdir(path)

        # 获取 SVN 状态
        files = run_svn_status()

        if not files:
            sys.exit(0)

        # 应用忽略模式
        config = load_config()
        ignore_patterns = config.get("ignorePatterns", [])
        files = apply_ignore_patterns(files, ignore_patterns)

        if not files:
            sys.exit(0)

        # 显示 GUI
        show_quick_pick(files)

    except Exception as e:
        print(f"启动 GUI 失败: {e}", file=sys.stderr)
        sys.exit(1)


def get_install_command() -> str:
    """
    获取右键菜单安装命令

    Returns:
        注册表命令字符串
    """
    # 检测是否为 PyInstaller 打包的 exe
    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        return f'"{exe_path}" --dir "%v"'

    # 开发环境：使用 Python 解释器
    python_exe = sys.executable
    install_dir = Path(__file__).parent.parent.parent.parent.resolve()
    install_dir_str = str(install_dir).replace("\\", "\\\\")
    python_code = (
        f"import sys; sys.path.insert(0, '{install_dir_str}'); "
        f"from smart_svn_commit.windows.context_menu_installer import handle_context_menu; "
        f"handle_context_menu('%v')"
    )
    return f'"{python_exe}" -c "{python_code}"'


def register_context_menu() -> bool:
    """
    注册右键菜单（文件夹背景 + 文件夹本身）

    Returns:
        是否成功
    """
    try:
        command = get_install_command()

        # 注册文件夹背景右键菜单
        if not set_registry_value(
            winreg.HKEY_CURRENT_USER, CONTEXT_MENU_BG_KEY_PATH, "", "Smart SVN Commit"
        ):
            return False
        if not set_registry_value(
            winreg.HKEY_CURRENT_USER, CONTEXT_MENU_BG_COMMAND_KEY_PATH, "", command
        ):
            return False

        # 注册文件夹右键菜单
        if not set_registry_value(
            winreg.HKEY_CURRENT_USER, CONTEXT_MENU_DIR_KEY_PATH, "", "Smart SVN Commit"
        ):
            return False
        if not set_registry_value(
            winreg.HKEY_CURRENT_USER, CONTEXT_MENU_DIR_COMMAND_KEY_PATH, "", command
        ):
            return False

        print("右键菜单已成功注册", file=sys.stderr)
        return True

    except Exception as e:
        print(f"注册右键菜单失败: {e}", file=sys.stderr)
        return False


def unregister_context_menu() -> bool:
    """
    卸载右键菜单（文件夹背景 + 文件夹本身）

    Returns:
        是否成功
    """
    try:
        # 删除文件夹背景菜单
        delete_registry_key(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_BG_COMMAND_KEY_PATH)
        delete_registry_key(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_BG_KEY_PATH)

        # 删除文件夹菜单
        delete_registry_key(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_DIR_COMMAND_KEY_PATH)
        delete_registry_key(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_DIR_KEY_PATH)

        print("右键菜单已成功卸载", file=sys.stderr)
        return True

    except Exception as e:
        print(f"卸载右键菜单失败: {e}", file=sys.stderr)
        return False


def is_context_menu_registered() -> bool:
    """
    检查右键菜单是否已注册

    Returns:
        是否已注册（任一路径存在即返回 True）
    """
    return registry_key_exists(
        winreg.HKEY_CURRENT_USER, CONTEXT_MENU_BG_KEY_PATH
    ) or registry_key_exists(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_DIR_KEY_PATH)


# 主入口（用于注册表命令调用）
if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_context_menu(sys.argv[1])
