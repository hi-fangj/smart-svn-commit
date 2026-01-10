"""
Windows 平台特定功能模块
"""

from .context_menu_installer import (
    register_context_menu,
    unregister_context_menu,
    is_context_menu_registered,
    is_svn_working_copy,
    handle_context_menu,
    register_com_context_menu,
    unregister_com_context_menu,
    is_com_context_menu_registered,
)

__all__ = [
    "register_context_menu",
    "unregister_context_menu",
    "is_context_menu_registered",
    "is_svn_working_copy",
    "handle_context_menu",
    "register_com_context_menu",
    "unregister_com_context_menu",
    "is_com_context_menu_registered",
]
