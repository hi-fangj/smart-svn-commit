"""
Windows 右键菜单安装模块
"""

import os
import subprocess
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
from .svn_helpers import get_install_dir, is_svn_working_copy

# COM 扩展模块路径
CONTEXT_MENU_EXTENSION_MODULE = "smart_svn_commit.windows.context_menu_extension"

# 右键菜单注册表路径配置
_MENU_REGISTRY_PATHS = {
    "background": (
        r"Software\Classes\Directory\Background\shell\smart-svn-commit",
        r"Software\Classes\Directory\Background\shell\smart-svn-commit\command",
    ),
    "directory": (
        r"Software\Classes\Directory\shell\smart-svn-commit",
        r"Software\Classes\Directory\shell\smart-svn-commit\command",
    ),
    "file": (
        r"Software\Classes\*\shell\smart-svn-commit",
        r"Software\Classes\*\shell\smart-svn-commit\command",
    ),
}

# 兼容旧版本的常量
CONTEXT_MENU_BG_KEY_PATH = _MENU_REGISTRY_PATHS["background"][0]
CONTEXT_MENU_BG_COMMAND_KEY_PATH = _MENU_REGISTRY_PATHS["background"][1]
CONTEXT_MENU_DIR_KEY_PATH = _MENU_REGISTRY_PATHS["directory"][0]
CONTEXT_MENU_DIR_COMMAND_KEY_PATH = _MENU_REGISTRY_PATHS["directory"][1]
CONTEXT_MENU_FILE_KEY_PATH = _MENU_REGISTRY_PATHS["file"][0]
CONTEXT_MENU_FILE_COMMAND_KEY_PATH = _MENU_REGISTRY_PATHS["file"][1]
CONTEXT_MENU_KEY_PATH = CONTEXT_MENU_BG_KEY_PATH
CONTEXT_MENU_COMMAND_KEY_PATH = CONTEXT_MENU_BG_COMMAND_KEY_PATH


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
        install_dir = get_install_dir()
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

        # 应用忽略模式
        config = load_config()
        ignore_patterns = config.get("ignorePatterns", [])
        files = apply_ignore_patterns(files, ignore_patterns)

        # 始终显示 GUI（即使没有变动）
        show_quick_pick(files)

    except Exception as e:
        print(f"启动 GUI 失败: {e}", file=sys.stderr)
        sys.exit(1)


def handle_file_context_menu(file_path: str) -> None:
    """
    处理文件右键菜单调用（从注册表命令调用）

    Args:
        file_path: 用户右键点击的文件路径
    """
    # 检查文件所在目录是否是 SVN 工作副本
    file = Path(file_path)
    parent_dir = file.parent

    if not is_svn_working_copy(str(parent_dir)):
        # 不是 SVN 工作副本，静默退出
        sys.exit(0)

    # 是 SVN 工作副本，启动 GUI 并显示该文件
    try:
        # 获取当前脚本所在目录的安装路径
        install_dir = get_install_dir()
        if (install_dir / "smart_svn_commit").exists():
            src_dir = install_dir / "src"
            sys.path.insert(0, str(src_dir))

        from smart_svn_commit.ui.main_window import show_quick_pick

        # 切换到文件所在目录
        os.chdir(parent_dir)

        # 创建单文件列表
        files = [("M", file.name)]

        # 显示 GUI
        show_quick_pick(files)

    except Exception as e:
        print(f"启动 GUI 失败: {e}", file=sys.stderr)
        sys.exit(1)


def get_install_command(menu_type: str = "dir") -> str:
    """
    获取右键菜单安装命令

    Args:
        menu_type: 菜单类型，"dir" 表示目录，"file" 表示文件

    Returns:
        注册表命令字符串
    """
    # 检测是否为 PyInstaller 打包的 exe
    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        flag = "%1" if menu_type == "file" else "%v"
        arg = "--file" if menu_type == "file" else "--dir"
        return f'"{exe_path}" {arg} "{flag}"'

    # 开发环境：使用 Python 解释器
    return _build_python_command(menu_type)


def _build_python_command(menu_type: str) -> str:
    """
    构建开发环境下的 Python 命令

    Args:
        menu_type: 菜单类型

    Returns:
        完整的 Python 命令字符串
    """
    python_exe = sys.executable
    install_dir = get_install_dir().resolve()
    install_dir_str = str(install_dir).replace("\\", "\\\\")

    flag = "%1" if menu_type == "file" else "%v"
    is_dir_param = "is_dir=False" if menu_type == "file" else "is_dir=True"

    python_code = (
        f"import sys; sys.path.insert(0, '{install_dir_str}'); "
        f"from smart_svn_commit.windows.menu_check import check_svn_and_launch; "
        f"check_svn_and_launch('{flag}', {is_dir_param})"
    )

    return f'"{python_exe}" -c "{python_code}"'


def register_context_menu() -> bool:
    """
    注册右键菜单（文件夹背景 + 文件夹本身 + 文件）

    Returns:
        是否成功
    """
    try:
        dir_command = get_install_command("dir")
        file_command = get_install_command("file")

        # 注册文件夹背景右键菜单
        if not _register_single_menu("background", dir_command):
            return False

        # 注册文件夹右键菜单
        if not _register_single_menu("directory", dir_command):
            return False

        # 注册文件右键菜单
        if not _register_single_menu("file", file_command):
            return False

        print("右键菜单已成功注册", file=sys.stderr)
        return True

    except Exception as e:
        print(f"注册右键菜单失败: {e}", file=sys.stderr)
        return False


def _register_single_menu(menu_type: str, command: str) -> bool:
    """
    注册单个菜单类型

    Args:
        menu_type: 菜单类型（background/directory/file）
        command: 注册表命令

    Returns:
        是否成功
    """
    key_path, command_key_path = _MENU_REGISTRY_PATHS[menu_type]

    if not set_registry_value(
        winreg.HKEY_CURRENT_USER, key_path, "", "Smart SVN Commit"
    ):
        return False

    if not set_registry_value(
        winreg.HKEY_CURRENT_USER, command_key_path, "", command
    ):
        return False

    return True


def unregister_context_menu() -> bool:
    """
    卸载右键菜单（文件夹背景 + 文件夹本身 + 文件）

    Returns:
        是否成功
    """
    try:
        # 删除所有菜单类型
        for menu_type in ("background", "directory", "file"):
            _unregister_single_menu(menu_type)

        print("右键菜单已成功卸载", file=sys.stderr)
        return True

    except Exception as e:
        print(f"卸载右键菜单失败: {e}", file=sys.stderr)
        return False


def _unregister_single_menu(menu_type: str) -> None:
    """
    卸载单个菜单类型

    Args:
        menu_type: 菜单类型（background/directory/file）
    """
    key_path, command_key_path = _MENU_REGISTRY_PATHS[menu_type]
    delete_registry_key(winreg.HKEY_CURRENT_USER, command_key_path)
    delete_registry_key(winreg.HKEY_CURRENT_USER, key_path)


def is_context_menu_registered() -> bool:
    """
    检查右键菜单是否已注册

    Returns:
        是否已注册（任一路径存在即返回 True）
    """
    return any(
        registry_key_exists(winreg.HKEY_CURRENT_USER, _MENU_REGISTRY_PATHS[menu_type][0])
        for menu_type in ("background", "directory", "file")
    )


# ============================================================================
# COM Shell Extension 注册/卸载函数
# ============================================================================

COM_MENU_KEY_PATHS = [
    r"Software\Classes\Directory\Background\shellex\ContextMenuHandlers\SmartSvnCommit",
    r"Software\Classes\Directory\shellex\ContextMenuHandlers\SmartSvnCommit",
    r"Software\Classes\*\shellex\ContextMenuHandlers\SmartSvnCommit",
]


def register_com_context_menu() -> bool:
    """
    注册 COM Shell Extension 右键菜单

    COM 扩展可以动态判断是否显示菜单项，只在 SVN 工作副本中显示

    Returns:
        是否成功
    """
    try:
        # PyInstaller 打包环境：直接调用注册函数
        if getattr(sys, "frozen", False):
            from smart_svn_commit.windows.context_menu_extension import DllRegisterServer

            DllRegisterServer()
        else:
            # 开发环境：通过 subprocess 执行脚本
            install_dir = get_install_dir().resolve()
            src_dir = install_dir / "src"
            extension_module = src_dir / "smart_svn_commit" / "windows" / "context_menu_extension.py"

            python_exe = sys.executable
            cmd = [python_exe, str(extension_module)]

            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, cwd=str(src_dir)
            )

        # 重启资源管理器
        _restart_explorer()

        print("COM Shell Extension 右键菜单已成功注册", file=sys.stderr)
        print("菜单项将只在 SVN 工作副本中显示", file=sys.stderr)
        return True

    except subprocess.CalledProcessError as e:
        print(f"注册 COM 扩展失败: {e}", file=sys.stderr)
        print(f"stdout: {e.stdout}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"注册 COM 扩展失败: {e}", file=sys.stderr)
        return False


def unregister_com_context_menu() -> bool:
    """
    卸载 COM Shell Extension 右键菜单

    Returns:
        是否成功
    """
    try:
        # PyInstaller 打包环境：直接调用卸载函数
        if getattr(sys, "frozen", False):
            from smart_svn_commit.windows.context_menu_extension import DllUnregisterServer

            DllUnregisterServer()
        else:
            # 开发环境：通过 subprocess 执行脚本
            install_dir = get_install_dir().resolve()
            src_dir = install_dir / "src"
            extension_module = src_dir / "smart_svn_commit" / "windows" / "context_menu_extension.py"

            python_exe = sys.executable
            cmd = [
                python_exe,
                str(extension_module),
                "--unregister",
            ]

            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, cwd=str(src_dir)
            )

        # 重启资源管理器
        _restart_explorer()

        print("COM Shell Extension 右键菜单已成功卸载", file=sys.stderr)
        return True

    except Exception as e:
        print(f"卸载 COM 扩展失败: {e}", file=sys.stderr)
        return False


def is_com_context_menu_registered() -> bool:
    """
    检查 COM Shell Extension 右键菜单是否已注册

    Returns:
        是否已注册
    """
    return any(
        registry_key_exists(winreg.HKEY_CURRENT_USER, key_path)
        for key_path in COM_MENU_KEY_PATHS
    )


def _restart_explorer() -> None:
    """重启 Windows 资源管理器以使更改生效"""
    try:
        # 通知资源管理器刷新设置
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            check=False,
            capture_output=True,
        )
        subprocess.run(["start", "explorer.exe"], shell=True, check=False)
    except Exception:
        pass


# 主入口（用于注册表命令调用）
if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_context_menu(sys.argv[1])
