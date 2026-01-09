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
    set_registry_value,
    delete_registry_key,
    registry_key_exists,
)


# 右键菜单注册表路径
CONTEXT_MENU_KEY_PATH = r"Software\Classes\Directory\Background\shell\smart-svn-commit"
CONTEXT_MENU_COMMAND_KEY_PATH = f"{CONTEXT_MENU_KEY_PATH}\\command"


def is_svn_working_copy(path: str) -> bool:
    """
    检查目录是否是 SVN 工作副本

    Args:
        path: 目录路径

    Returns:
        是否是 SVN 工作副本
    """
    svn_dir = Path(path) / ".svn"
    return svn_dir.is_dir()


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

        from smart_svn_commit.ui.main_window import show_quick_pick
        from smart_svn_commit.core.parser import parse_svn_status
        from smart_svn_commit.core.commit import run_svn_status
        from smart_svn_commit.utils.filters import apply_ignore_patterns
        from smart_svn_commit.core.config import load_config

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
    # 获取 Python 可执行文件路径
    python_exe = sys.executable

    # 获取安装目录
    install_dir = Path(__file__).parent.parent.parent.parent.resolve()

    # 构建命令：python -c "import sys; sys.path.insert(0, 'INSTALL_DIR'); from smart_svn_commit.windows.context_menu_installer import handle_context_menu; handle_context_menu('%V')"
    # 注意：注册表中的 %v 会被替换为用户右键点击的目录路径
    install_dir_str = str(install_dir).replace('\\', '\\\\')
    python_code = (
        f"import sys; sys.path.insert(0, '{install_dir_str}'); "
        f"from smart_svn_commit.windows.context_menu_installer import handle_context_menu; "
        f"handle_context_menu('%v')"
    )
    command = f'"{python_exe}" -c "{python_code}"'

    return command


def register_context_menu() -> bool:
    """
    注册右键菜单

    Returns:
        是否成功
    """
    try:
        # 创建菜单项键
        if not set_registry_value(
            winreg.HKEY_CURRENT_USER,
            CONTEXT_MENU_KEY_PATH,
            "",
            "Smart SVN Commit"
        ):
            return False

        # 设置图标（可选）
        # set_registry_value(
        #     winreg.HKEY_CURRENT_USER,
        #     CONTEXT_MENU_KEY_PATH,
        #     "Icon",
        #     str(Path(sys.executable).parent / "python.exe")
        # )

        # 设置命令
        command = get_install_command()
        if not set_registry_value(
            winreg.HKEY_CURRENT_USER,
            CONTEXT_MENU_COMMAND_KEY_PATH,
            "",
            command
        ):
            return False

        print("右键菜单已成功注册", file=sys.stderr)
        return True

    except Exception as e:
        print(f"注册右键菜单失败: {e}", file=sys.stderr)
        return False


def unregister_context_menu() -> bool:
    """
    卸载右键菜单

    Returns:
        是否成功
    """
    try:
        # 删除命令键
        delete_registry_key(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_COMMAND_KEY_PATH)

        # 删除菜单项键
        delete_registry_key(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_KEY_PATH)

        print("右键菜单已成功卸载", file=sys.stderr)
        return True

    except Exception as e:
        print(f"卸载右键菜单失败: {e}", file=sys.stderr)
        return False


def is_context_menu_registered() -> bool:
    """
    检查右键菜单是否已注册

    Returns:
        是否已注册
    """
    return registry_key_exists(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_KEY_PATH)


# 主入口（用于注册表命令调用）
if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_context_menu(sys.argv[1])
