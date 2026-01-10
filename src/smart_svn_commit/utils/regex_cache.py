"""
正则表达式缓存
"""

import re
from typing import Dict, Pattern


class RegexCache:
    """正则表达式缓存，避免重复编译相同的模式"""

    def __init__(self):
        self._cache: Dict[str, Pattern] = {}

    def get(self, pattern: str) -> Pattern:
        """
        获取编译后的正则表达式，如果不存在则编译并缓存

        Args:
            pattern: 正则表达式字符串

        Returns:
            编译后的正则表达式对象
        """
        if pattern not in self._cache:
            self._cache[pattern] = re.compile(pattern, re.IGNORECASE)
        return self._cache[pattern]

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()


# 全局单例实例
_global_cache = RegexCache()


def get_global_cache() -> RegexCache:
    """获取全局正则缓存实例"""
    return _global_cache
