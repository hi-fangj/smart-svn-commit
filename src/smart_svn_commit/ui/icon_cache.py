"""
图标缓存模块

提供文件类型图标获取和缓存功能（支持 LRU 限制）
"""

from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyle, QFileIconProvider


class IconCache:
    """图标缓存，避免重复获取相同类型的图标（支持 LRU 限制）"""

    # 默认最大缓存大小
    DEFAULT_MAX_SIZE = 100

    def __init__(self, parent_style=None, max_size: int = DEFAULT_MAX_SIZE):
        """
        初始化图标缓存

        Args:
            parent_style: 父控件的 style 对象，用于获取标准图标
            max_size: 最大缓存大小，默认 100
        """
        self._cache: Dict[str, QIcon] = {}
        self._max_size = max_size
        self._access_order: List[str] = []
        self._icon_provider = QFileIconProvider()
        self._style = parent_style

    def get(self, file_path: str) -> QIcon:
        """
        获取文件图标（带 LRU 缓存）

        Args:
            file_path: 文件路径

        Returns:
            文件图标
        """
        cache_key = self._get_cache_key(file_path)

        if cache_key not in self._cache:
            self._ensure_cache_size()
            self._cache[cache_key] = self._fetch_icon(file_path)

        # 更新访问顺序（LRU）
        self._update_access_order(cache_key)

        return self._cache[cache_key]

    def _update_access_order(self, cache_key: str) -> None:
        """
        更新访问顺序（将缓存键移到末尾）

        Args:
            cache_key: 缓存键
        """
        if cache_key in self._access_order:
            self._access_order.remove(cache_key)
        self._access_order.append(cache_key)

    def _ensure_cache_size(self) -> None:
        """确保缓存不超过最大大小（LRU 淘汰）"""
        while len(self._cache) >= self._max_size:
            oldest = self._access_order.pop(0)
            del self._cache[oldest]

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
        获取图标（按后缀名获取，不检查文件是否存在）

        优先级：
        1. 系统图标（QFileIconProvider，按后缀名/类型获取）
        2. 标准图标（QStyle）
        3. 空图标

        Args:
            file_path: 文件路径

        Returns:
            图标对象
        """
        try:
            file_info = QFileInfo(file_path)

            # 直接根据类型获取图标（不检查文件是否存在）
            if file_info.isDir():
                icon = self._icon_provider.icon(QFileIconProvider.Folder)
            else:
                # 按文件扩展名获取类型图标
                icon = self._icon_provider.icon(file_info)

            if not icon.isNull():
                return icon
        except (RuntimeError, OSError):
            pass

        # 降级到标准图标
        if self._style:
            return self._style.standardIcon(QStyle.SP_FileIcon)

        # 最后的降级：空图标
        return QIcon()

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._access_order.clear()

    @property
    def size(self) -> int:
        """获取当前缓存大小"""
        return len(self._cache)


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
