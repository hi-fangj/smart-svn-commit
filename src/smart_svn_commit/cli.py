"""
命令行入口点
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any

from .core.parser import parse_svn_status
from .core.commit import execute_svn_commit, run_svn_status
from .core.config import load_config, init_config, get_config_path
from .utils.filters import apply_ignore_patterns
from .ai.factory import generate_commit_message

# 尝试导入 UI 模块
try:
    from .ui.main_window import show_quick_pick

    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False

# 尝试导入 Windows 模块
WINDOWS_AVAILABLE = sys.platform == "win32"
if WINDOWS_AVAILABLE:
    try:
        from .windows import (
            register_context_menu,
            unregister_context_menu,
            is_context_menu_registered,
        )
    except ImportError:
        WINDOWS_AVAILABLE = False


def output_result(result: Dict[str, Any]) -> None:
    """
    输出 JSON 格式结果

    Args:
        result: 包含 selected、commitMessage、cancelled 的字典
    """
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> int:
    """主 CLI 入口"""
    parser = argparse.ArgumentParser(
        description="Smart SVN Commit - AI 驱动的 SVN 提交助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 自动检测 SVN 状态并显示 GUI
    smart-svn-commit

    # 指定文件列表
    smart-svn-commit --files="file1.cs,file2.cs"

    # 从 SVN 管道
    svn status | smart-svn-commit --status

    # 跳过 GUI
    smart-svn-commit --files="file1.cs,file2.cs" --skip-ui

    # 配置管理
    smart-svn-commit --config init
    smart-svn-commit --config show

依赖:
    pip install PyQt5
    pip install openai  # 可选，用于 AI 生成提交消息
        """,
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    parser.add_argument("--files", type=str, help="逗号分隔的文件列表")

    parser.add_argument("--status", action="store_true", help="从 stdin 读取 SVN 状态输出")

    parser.add_argument(
        "--skip-ui", action="store_true", help="跳过 GUI 界面，直接使用提供的文件列表"
    )

    parser.add_argument("--ignore", type=str, help="逗号分隔的忽略模式（覆盖配置文件）")

    parser.add_argument("--no-ignore", action="store_true", help="禁用所有忽略模式")

    parser.add_argument("--config", type=str, choices=["init", "edit", "show"], help="配置管理操作")

    parser.add_argument(
        "--context-menu",
        type=str,
        choices=["install", "uninstall", "status"],
        help="Windows 右键菜单管理（仅 Windows）",
    )

    parser.add_argument("--file", type=str, help="打开 GUI 并显示指定文件")

    parser.add_argument("--dir", type=str, help="打开 GUI 并显示目录下变更文件")

    args = parser.parse_args()

    # 处理右键菜单命令
    if args.context_menu:
        if not WINDOWS_AVAILABLE:
            print("错误: 右键菜单功能仅支持 Windows 平台", file=sys.stderr)
            return 1

        if args.context_menu == "install":
            if register_context_menu():
                return 0
            else:
                return 1
        elif args.context_menu == "uninstall":
            if unregister_context_menu():
                return 0
            else:
                return 1
        elif args.context_menu == "status":
            if is_context_menu_registered():
                print("右键菜单已注册")
                return 0
            else:
                print("右键菜单未注册")
                return 1

    # 处理配置命令
    if args.config == "init":
        config_path = init_config()
        print(f"配置文件已创建: {config_path}")
        print("请编辑配置文件，设置 AI API 密钥等信息。")
        return 0
    elif args.config == "show":
        config = load_config()
        print(json.dumps(config, ensure_ascii=False, indent=2))
        return 0
    elif args.config == "edit":
        import os
        import subprocess

        config_path = get_config_path()
        if not config_path.exists():
            config_path = init_config()
        # 使用系统默认编辑器打开
        if sys.platform == "win32":
            os.startfile(config_path)
        else:
            editor = os.environ.get("EDITOR", "vi")
            subprocess.call([editor, config_path])
        return 0

    # 处理 --file 参数
    if args.file:
        if not UI_AVAILABLE:
            print("错误: PyQt5 未安装，无法使用 GUI", file=sys.stderr)
            return 1
        # 切换到文件所在目录
        file_path = Path(args.file).resolve()
        os.chdir(file_path.parent)
        # 创建单文件列表
        files = [("M", str(file_path.name))]
        result = show_quick_pick(files)
        output_result(result)
        return 0 if not result.get("cancelled") else 1

    # 处理 --dir 参数
    if args.dir:
        if not UI_AVAILABLE:
            print("错误: PyQt5 未安装，无法使用 GUI", file=sys.stderr)
            return 1
        # 切换到指定目录
        dir_path = Path(args.dir).resolve()
        if not dir_path.is_dir():
            print(f"错误: 目录不存在: {args.dir}", file=sys.stderr)
            return 1
        os.chdir(dir_path)
        # 获取该目录的 SVN 状态
        files = run_svn_status()
        if not files:
            output_result({"selected": [], "commitMessage": "", "cancelled": True})
            return 0
        # 应用忽略模式
        config = load_config()
        ignore_patterns = config.get("ignorePatterns", [])
        files = apply_ignore_patterns(files, ignore_patterns)
        if not files:
            output_result({"selected": [], "commitMessage": "", "cancelled": False})
            return 0
        result = show_quick_pick(files)
        output_result(result)
        return 0 if not result.get("cancelled") else 1

    # 收集文件列表
    files = _collect_files(args)

    if not files:
        output_result({"selected": [], "commitMessage": "", "cancelled": True})
        return 0

    # 应用忽略过滤
    files = _apply_ignore_filters(files, args)

    if not files:
        output_result({"selected": [], "commitMessage": "", "cancelled": False})
        return 0

    # 获取选中的文件和提交消息
    result = _get_selected_files(files, args)

    # 输出结果
    output_result(result)

    return 0 if not result.get("cancelled") else 1


def _collect_files(args) -> List[Tuple[str, str]]:
    """
    收集文件列表（带状态）

    Args:
        args: 命令行参数

    Returns:
        (状态, 文件路径) 元组列表
    """
    files: List[Tuple[str, str]] = []

    if args.files:
        # 直接指定的文件，默认为修改状态
        file_list = [f.strip() for f in args.files.split(",") if f.strip()]
        files.extend(("M", f) for f in file_list)

    if args.status:
        # 从 stdin 读取 SVN 状态
        if not sys.stdin.isatty():
            status_output = sys.stdin.read()
            if status_output.strip():
                files.extend(parse_svn_status(status_output))

    # 只在没有提供任何输入时才自动执行 svn status
    if not files and not args.files and not args.status:
        files = run_svn_status()

    return files


def _apply_ignore_filters(files: List[Tuple[str, str]], args) -> List[Tuple[str, str]]:
    """
    应用忽略模式过滤文件列表

    Args:
        files: (状态, 文件路径) 元组列表
        args: 命令行参数

    Returns:
        过滤后的文件列表
    """
    # 加载配置
    config = load_config()
    ignore_patterns = config.get("ignorePatterns", [])

    # 应用命令行覆盖
    if args.ignore:
        ignore_patterns = [p.strip() for p in args.ignore.split(",") if p.strip()]

    # 应用忽略模式
    if not args.no_ignore and ignore_patterns:
        files = apply_ignore_patterns(files, ignore_patterns)

    return files


def _get_selected_files(files: List[Tuple[str, str]], args) -> Dict[str, Any]:
    """
    获取选中的文件列表和提交消息

    Args:
        files: (状态, 文件路径) 元组列表
        args: 命令行参数

    Returns:
        包含 selected、commitMessage、cancelled、commitResult 的字典
    """
    if args.skip_ui:
        # 跳过 UI 模式：自动生成提交消息
        selected = [path for _, path in files]
        commit_msg = generate_commit_message(selected)
        return {
            "selected": selected,
            "commitMessage": commit_msg,
            "cancelled": False,
            "commitResult": None,  # skip-ui 模式不执行提交
        }
    else:
        if not UI_AVAILABLE:
            print(
                json.dumps(
                    {
                        "error": "PyQt5 not installed",
                        "message": "请运行: pip install PyQt5",
                        "available": [path for _, path in files],
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return {"selected": [], "commitMessage": "", "cancelled": True, "commitResult": None}
        return show_quick_pick(files)


if __name__ == "__main__":
    sys.exit(main())
