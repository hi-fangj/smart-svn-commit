"""
Windows COM Shell Extension for Smart SVN Commit
实现动态右键菜单，只在 SVN 工作副本中显示
"""

import os
import sys
import pythoncom
import win32con
import win32gui
import win32api
import win32process
from pathlib import Path

# 确保只有在 Windows 上才导入
if sys.platform == "win32":
    from win32com.shell import shell, shellcon
    import winerror

    try:
        from win32com.server.exception import COMException
    except ImportError:
        # 旧版本 pywin32 可能没有这个
        COMException = Exception


# COM 组件的 CLSID（请使用 GUID 生成器生成唯一的 ID）
# {7C5E5F3D-E8F3-4A8B-9C2D-3F5E6D7C8B9A}
CLSID_SVN_CONTEXT_MENU = "{7C5E5F3D-E8F3-4A8B-9C2D-3F5E6D7C8B9A}"


def is_svn_working_copy(path: str) -> bool:
    """
    检查目录是否是 SVN 工作副本

    Args:
        path: 目录路径

    Returns:
        是否是 SVN 工作副本
    """
    try:
        return (Path(path) / ".svn").is_dir()
    except Exception:
        return False


def get_install_dir() -> Path:
    """获取安装目录"""
    return Path(__file__).parent.parent.parent.parent


class SVNContextMenuExtension:
    """
    Smart SVN Commit 右键菜单扩展

    实现动态右键菜单，只在 SVN 工作副本中显示菜单项
    """

    _reg_clsid_ = CLSID_SVN_CONTEXT_MENU
    _reg_progid_ = "SmartSvnCommit.ContextMenu"
    _reg_desc_ = "Smart SVN Commit Context Menu Extension"
    _com_interfaces_ = [
        shell.IID_IShellExtInit,
        shell.IID_IContextMenu,
    ]
    _public_methods_ = (
        shellcon.IContextMenu_Methods + shellcon.IShellExtInit_Methods
    )

    def __init__(self):
        self.m_selected_files = []
        self.m_is_svn_working_copy = False
        self.m_hwnd = None

    # ========================================================================
    # IShellExtInit 接口实现
    # ========================================================================

    def Initialize(self, folder, data_obj, hkey_prog_id):
        """
        初始化 Shell 扩展

        Args:
            folder: 文件夹的 ITEMIDLIST
            data_obj: 包含选中文件的数据对象
            hkey_prog_id: 文件类型的注册表键

        Returns:
            HRESULT
        """
        self.m_selected_files = []
        self.m_is_svn_working_copy = False

        try:
            # 从数据对象获取选中的文件
            if data_obj is None:
                return winerror.E_FAIL

            # 使用 FORMATETC 和 STGMEDIUM 获取文件列表
            format_etc = (
                shellcon.SHCLSID_ShellExtension,
                None,
                pythoncom.DVASPECT_CONTENT,
                -1,
                pythoncom.TYMED_HGLOBAL,
            )

            try:
                # 尝试获取文件列表
                medium = data_obj.GetData(format_etc)
                if medium is None:
                    # 尝试另一种格式
                    format_etc = (
                        pythoncom.IID_IUnknown,
                        None,
                        pythoncom.DVASPECT_CONTENT,
                        -1,
                        pythoncom.TYMED_HGLOBAL,
                    )
                    medium = data_obj.GetData(format_etc)

                if medium and medium.data:
                    # 解析文件列表
                    drop_files = pythoncom.StgMediumData(medium)
                    if drop_files:
                        # DROPFILES 结构
                        import struct

                        # 获取文件列表
                        files = shell.DragQueryFile(drop_files.data, -1)
                        for i in range(files):
                            file_path = shell.DragQueryFile(drop_files.data, i)
                            self.m_selected_files.append(file_path)

            except Exception as e:
                # 如果获取失败，尝试使用 DragQueryFile
                pass

            # 检查是否是 SVN 工作副本
            if self.m_selected_files:
                # 检查第一个文件所在目录
                first_file = Path(self.m_selected_files[0])
                if first_file.is_dir():
                    check_path = first_file
                else:
                    check_path = first_file.parent

                self.m_is_svn_working_copy = is_svn_working_copy(str(check_path))

            return winerror.S_OK

        except Exception as e:
            print(f"Initialize error: {e}", file=sys.stderr)
            return winerror.E_FAIL

    # ========================================================================
    # IContextMenu 接口实现
    # ========================================================================

    def QueryContextMenu(self, hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags):
        """
        向菜单中添加菜单项

        Args:
            hMenu: 菜单句柄
            indexMenu: 插入菜单项的索引位置
            idCmdFirst: 第一个命令 ID
            idCmdLast: 最后一个命令 ID
            uFlags: 标志位

        Returns:
            HRESULT，表示添加的菜单项数量
        """
        # 如果不是 SVN 工作副本，不添加菜单项
        if not self.m_is_svn_working_copy:
            return winerror.S_OK

        # 检查标志位，如果 CMF_DEFAULTONLY 设置，则不添加自定义菜单项
        if uFlags & shellcon.CMF_DEFAULTONLY:
            return winerror.S_OK

        try:
            # 创建菜单项
            menu_item = "Smart SVN Commit"
            icon_index = 0

            # 插入菜单项
            win32gui.InsertMenu(
                hMenu,
                indexMenu,
                win32con.MF_STRING | win32con.MF_BYPOSITION,
                idCmdFirst,
                menu_item,
            )

            # 返回添加的菜单项数量
            return 1  # 返回 1 表示添加了 1 个菜单项

        except Exception as e:
            print(f"QueryContextMenu error: {e}", file=sys.stderr)
            return winerror.E_FAIL

    def InvokeCommand(self, ci):
        """
        处理菜单命令点击

        Args:
            ci: CMINVOKECOMMANDINFO 结构

        Returns:
            HRESULT
        """
        try:
            # 检查命令类型
            if isinstance(ci.lpVerb, int):
                # 如果是命令 ID
                if ci.lpVerb != 0:
                    return winerror.E_INVALIDARG
            else:
                # 如果是命令字符串
                if ci.lpVerb.lower() != "smartsvncommit":
                    return winerror.E_INVALIDARG

            # 获取安装目录
            install_dir = get_install_dir()

            # 构建 Python 命令
            if getattr(sys, "frozen", False):
                # PyInstaller 打包版本
                exe_path = sys.executable
            else:
                # 开发环境
                exe_path = sys.executable

            # 构建命令参数
            if self.m_selected_files:
                first_file = self.m_selected_files[0]
                file_path = Path(first_file)

                if file_path.is_dir():
                    args = ["--dir", first_file]
                else:
                    args = ["--file", first_file]

                # 启动主程序
                cmd = [exe_path] + args

                # 使用 ShellExecute 启动程序
                import subprocess

                subprocess.Popen(
                    cmd,
                    creationflags=win32process.CREATE_NO_WINDOW,
                    close_fds=True,
                )

            return winerror.S_OK

        except Exception as e:
            print(f"InvokeCommand error: {e}", file=sys.stderr)
            # 显示错误消息
            try:
                win32gui.MessageBox(
                    0, f"启动失败: {e}", "Smart SVN Commit", win32con.MB_ICONERROR
                )
            except Exception:
                pass
            return winerror.E_FAIL

    def GetCommandString(self, cmd, uType):
        """
        获取命令的文本信息

        Args:
            cmd: 命令 ID
            uType: 标志位，指定返回的文本类型

        Returns:
            文本字符串
        """
        try:
            if uType == shellcon.GCS_HELPTEXTA:
                # ANSI 帮助文本
                return "使用 AI 生成 SVN 提交消息"
            elif uType == shellcon.GCS_HELPTEXTW:
                # Unicode 帮助文本
                return "使用 AI 生成 SVN 提交消息"
            elif uType == shellcon.GCS_VERBA:
                # ANSI 动词
                return "SmartSvnCommit"
            elif uType == shellcon.GCS_VERBW:
                # Unicode 动词
                return "SmartSvnCommit"
            elif uType == shellcon.GCS_VALIDATEA or uType == shellcon.GCS_VALIDATEW:
                # 验证
                return winerror.S_OK

            return winerror.E_INVALIDARG

        except Exception as e:
            print(f"GetCommandString error: {e}", file=sys.stderr)
            return winerror.E_INVALIDARG


def DllRegisterServer():
    """
    注册 COM 组件
    """
    import win32com.server.register

    # 注册 COM 组件
    win32com.server.register.UseCommandLine(SVNContextMenuExtension)

    # 注册右键菜单处理程序
    # 文件夹背景
    key_path = r"Software\Classes\Directory\Background\shellex\ContextMenuHandlers\SmartSvnCommit"
    try:
        key = win32api.RegCreateKey(win32con.HKEY_CURRENT_USER, key_path)
        win32api.RegSetValueEx(key, None, 0, win32con.REG_SZ, CLSID_SVN_CONTEXT_MENU)
        win32api.RegCloseKey(key)
    except Exception as e:
        print(f"注册文件夹背景菜单失败: {e}", file=sys.stderr)

    # 文件夹
    key_path = r"Software\Classes\Directory\shellex\ContextMenuHandlers\SmartSvnCommit"
    try:
        key = win32api.RegCreateKey(win32con.HKEY_CURRENT_USER, key_path)
        win32api.RegSetValueEx(key, None, 0, win32con.REG_SZ, CLSID_SVN_CONTEXT_MENU)
        win32api.RegCloseKey(key)
    except Exception as e:
        print(f"注册文件夹菜单失败: {e}", file=sys.stderr)

    # 文件
    key_path = r"Software\Classes\*\shellex\ContextMenuHandlers\SmartSvnCommit"
    try:
        key = win32api.RegCreateKey(win32con.HKEY_CURRENT_USER, key_path)
        win32api.RegSetValueEx(key, None, 0, win32con.REG_SZ, CLSID_SVN_CONTEXT_MENU)
        win32api.RegCloseKey(key)
    except Exception as e:
        print(f"注册文件菜单失败: {e}", file=sys.stderr)

    print("COM Shell Extension 已注册", file=sys.stderr)
    print("请重启 Windows 资源管理器以使更改生效", file=sys.stderr)


def DllUnregisterServer():
    """
    卸载 COM 组件
    """
    import win32com.server.register

    # 卸载 COM 组件
    win32com.server.register.UseCommandLine(SVNContextMenuExtension)

    # 删除右键菜单处理程序注册
    keys_to_delete = [
        r"Software\Classes\Directory\Background\shellex\ContextMenuHandlers\SmartSvnCommit",
        r"Software\Classes\Directory\shellex\ContextMenuHandlers\SmartSvnCommit",
        r"Software\Classes\*\shellex\ContextMenuHandlers\SmartSvnCommit",
    ]

    for key_path in keys_to_delete:
        try:
            win32api.RegDeleteKey(win32con.HKEY_CURRENT_USER, key_path)
        except Exception as e:
            pass  # 键不存在，忽略

    print("COM Shell Extension 已卸载", file=sys.stderr)
    print("请重启 Windows 资源管理器以使更改生效", file=sys.stderr)


if __name__ == "__main__":
    import win32com.server.register

    # 通过命令行参数控制注册/卸载
    win32com.server.register.UseCommandLine(SVNContextMenuExtension)
