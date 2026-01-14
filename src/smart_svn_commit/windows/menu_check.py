"""
Windows 右键菜单检查入口
快速检查是否是 SVN 工作副本，如果是则调用主程序，否则静默退出
"""

import os
import sys
from pathlib import Path

print(f"[menu_check.py] 模块加载开始", file=sys.stderr)
print(f"[menu_check.py] sys.executable: {sys.executable}", file=sys.stderr)
print(f"[menu_check.py] sys.argv: {sys.argv}", file=sys.stderr)

# 获取当前脚本所在目录的安装路径
install_dir = Path(__file__).parent.parent.parent
print(f"[menu_check.py] install_dir: {install_dir}", file=sys.stderr)

if (install_dir / "smart_svn_commit").exists():
    src_dir = install_dir / "src"
    sys.path.insert(0, str(src_dir))
    print(f"[menu_check.py] 添加 src_dir 到 path: {src_dir}", file=sys.stderr)

print("[menu_check.py] 模块加载完成", file=sys.stderr)


def check_svn_and_launch(file_path: str, is_dir: bool = False) -> None:
    """
    检查是否是 SVN 工作副本，如果是则启动主程序

    Args:
        file_path: 文件或目录路径
        is_dir: 是否是目录
    """
    # 确定要检查的目录
    if is_dir:
        check_path = Path(file_path)
    else:
        check_path = Path(file_path).parent

    # 快速检查是否是 SVN 工作副本
    svn_dir = check_path / ".svn"
    if not svn_dir.is_dir():
        # 不是 SVN 工作副本，静默退出（菜单项不会显示）
        print(f"[check_svn_and_launch] 不是 SVN 工作副本，退出", file=sys.stderr)
        sys.exit(0)

    # 是 SVN 工作副本，启动主程序
    try:
        print("[check_svn_and_launch] 导入 cli.main...", file=sys.stderr)
        from smart_svn_commit.cli import main

        # 修改 sys.argv 来传递正确的参数
        if is_dir:
            sys.argv = [sys.argv[0], "--dir", file_path]
        else:
            sys.argv = [sys.argv[0], "--file", file_path]

        print(f"[check_svn_and_launch] sys.argv: {sys.argv}", file=sys.stderr)
        print("[check_svn_and_launch] 调用 main()", file=sys.stderr)

        # 调用主程序
        sys.exit(main())

    except Exception as e:
        print(f"[check_svn_and_launch] 启动失败: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    # 检测调用类型
    # 如果参数以 -- 开头，说明是直接调用
    # 如果是纯路径，说明是从注册表调用
    arg = sys.argv[1]

    if arg == "--dir" and len(sys.argv) > 2:
        check_svn_and_launch(sys.argv[2], is_dir=True)
    elif arg == "--file" and len(sys.argv) > 2:
        check_svn_and_launch(sys.argv[2], is_dir=False)
    else:
        # 从注册表调用，需要判断是文件还是目录
        # 文件路径使用 %1，目录路径使用 %v
        if "\t" in arg or "\n" in arg:
            # 可能是多个文件，暂不支持
            sys.exit(0)

        path_obj = Path(arg)
        if path_obj.is_dir():
            check_svn_and_launch(arg, is_dir=True)
        else:
            check_svn_and_launch(arg, is_dir=False)
