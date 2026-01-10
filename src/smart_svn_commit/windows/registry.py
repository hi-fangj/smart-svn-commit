"""
Windows 注册表操作模块
"""

import sys
import winreg
from typing import Optional


def get_registry_value(
    hive: int, key_path: str, value_name: str, default: Optional[str] = None
) -> Optional[str]:
    """
    读取注册表值

    Args:
        hive: 注册表根键（如 HKEY_CURRENT_USER）
        key_path: 键路径
        value_name: 值名称
        default: 默认值（如果键不存在）

    Returns:
        注册表值，或默认值
    """
    try:
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
    except OSError:
        return default


def set_registry_value(hive: int, key_path: str, value_name: str, value: str) -> bool:
    """
    设置注册表值

    Args:
        hive: 注册表根键（如 HKEY_CURRENT_USER）
        key_path: 键路径
        value_name: 值名称
        value: 值

    Returns:
        是否成功
    """
    try:
        with winreg.CreateKeyEx(hive, key_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)
        return True
    except OSError as e:
        print(f"注册表写入失败: {e}", file=sys.stderr)
        return False


def delete_registry_key(hive: int, key_path: str) -> bool:
    """
    删除注册表键（递归）

    Args:
        hive: 注册表根键（如 HKEY_CURRENT_USER）
        key_path: 键路径

    Returns:
        是否成功
    """
    try:
        winreg.DeleteKey(hive, key_path)
        return True
    except OSError:
        # 尝试递归删除子键
        try:
            i = 0
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as key:
                while True:
                    subkey_name = winreg.EnumKey(key, i)
                    delete_registry_key(hive, f"{key_path}\\{subkey_name}")
                    i += 1
        except OSError:
            pass
        try:
            winreg.DeleteKey(hive, key_path)
            return True
        except OSError as e:
            print(f"注册表删除失败: {e}", file=sys.stderr)
            return False


def registry_key_exists(hive: int, key_path: str) -> bool:
    """
    检查注册表键是否存在

    Args:
        hive: 注册表根键（如 HKEY_CURRENT_USER）
        key_path: 键路径

    Returns:
        键是否存在
    """
    try:
        winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
        return True
    except WindowsError:
        return False
