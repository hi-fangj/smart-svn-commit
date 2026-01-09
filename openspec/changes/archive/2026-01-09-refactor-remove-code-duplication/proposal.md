# 变更：消除代码重复，统一共享工具类

## 为什么

当前代码库中存在严重的代码重复问题：
- `core/fs_helper.py` 和 `ui/fs_helper.py` 是完全相同的 `FileSystemHelper` 类
- `core/svn_executor.py` 和 `ui/svn_executor.py` 是几乎相同的 `SVNCommandExecutor` 类
- `utils/regex_cache.py` 和 `ui/regex_cache.py` 是几乎相同的 `RegexCache` 类

这违反了 DRY（Don't Repeat Yourself）原则，导致：
1. 维护负担：任何修改需要同步更新多个文件
2. 潜在的不一致：修改一个文件而忘记另一个会导致行为差异
3. 代码膨胀：增加代码库大小而无实际价值

## 变更内容

### 删除重复文件
- 删除 `ui/fs_helper.py`（使用 `core/fs_helper.py`）
- 删除 `ui/svn_executor.py`（使用 `core/svn_executor.py`）
- 删除 `ui/regex_cache.py`（使用 `utils/regex_cache.py`）

### 更新导入
- 更新 `ui/main_window.py` 中的导入语句，从 `core` 和 `utils` 导入共享类
- 更新 `ui/context_menu.py` 中的类型注解导入

### 规范化 API
- 统一 `utils/regex_cache.py` 的导出接口（添加 `get_global_cache` 函数）
- 确保 `core/` 模块中的类被正确导出

## 影响

### 受影响的规范
- 无现有规范（这是首次定义模块结构规范）

### 受影响的代码
- `ui/main_window.py` - 导入语句更改
- `ui/context_menu.py` - 类型注解更改
- `ui/fs_helper.py` - 删除
- `ui/svn_executor.py` - 删除
- `ui/regex_cache.py` - 删除
- `core/__init__.py` - 确认导出
- `utils/__init__.py` - 确认导出

### 重大变更
无。这是纯内部重构，不改变任何外部行为或 API。
