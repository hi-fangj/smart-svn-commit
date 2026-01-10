"""
图标缓存模块

提供文件类型图标获取和缓存功能
"""

from pathlib import Path
from typing import Dict, Optional

from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyle, QFileIconProvider


class IconCache:
    """图标缓存，避免重复获取相同类型的图标"""

    def __init__(self, parent_style=None):
        """
        初始化图标缓存

        Args:
            parent_style: 父控件的 style 对象，用于获取标准图标
        """
        self._cache: Dict[str, QIcon] = {}
        self._icon_provider = QFileIconProvider()
        self._style = parent_style

    def get(self, file_path: str) -> QIcon:
        """
        获取文件图标（带缓存）

        Args:
            file_path: 文件路径

        Returns:
            文件图标
        """
        cache_key = self._get_cache_key(file_path)

        if cache_key not in self._cache:
            self._cache[cache_key] = self._fetch_icon(file_path)

        return self._cache[cache_key]

    def _get_cache_key(self, file_path: str) -> str:
        """
        生成缓存键

        Args:
            file_path: 文件路径

        Returns:
            缓存键字符串
        """
        path_obj = Path(file_path)

        if path_obj.is_dir():
            return "dir:folder"

        ext = path_obj.suffix.lower()
        return f"ext:{ext}" if ext else "unknown"

    def _fetch_icon(self, file_path: str) -> QIcon:
        """
        获取图标

        优先级：
        1. 系统图标（QFileIconProvider，文件存在时）
        2. 根据文件类型获取系统图标（文件不存在时）
        3. 标准图标（QStyle）
        4. 空图标

        Args:
            file_path: 文件路径

        Returns:
            图标对象
        """
        try:
            file_info = QFileInfo(file_path)

            # 1. 如果文件存在，直接使用系统图标
            if file_info.exists():
                icon = self._icon_provider.icon(file_info)
                if not icon.isNull():
                    return icon

            # 2. 文件不存在时，根据类型获取系统图标
            if file_info.isDir():
                icon = self._icon_provider.icon(QFileIconProvider.Folder)
            else:
                # 对于文件，尝试根据扩展名获取图标
                # 创建一个临时文件名来获取对应的类型图标
                icon = self._icon_provider.icon(file_info)

            if not icon.isNull():
                return icon
        except Exception:
            pass

        # 3. 降级到标准图标
        if self._style:
            return self._style.standardIcon(QStyle.SP_FileIcon)

        # 4. 最后的降级：空图标
        return QIcon()

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()


# 全局单例实例
_global_icon_cache: Optional[IconCache] = None


def get_global_icon_cache(parent_style=None) -> IconCache:
    """
    获取全局图标缓存实例

    Args:
        parent_style: 父控件的 style 对象

    Returns:
        全局图标缓存实例
    """
    global _global_icon_cache
    if _global_icon_cache is None:
        _global_icon_cache = IconCache(parent_style)
    return _global_icon_cache
