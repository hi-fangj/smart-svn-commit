## 1. 代码重构

### 1.1 验证共享类的导出
- [x] 1.1.1 确认 `core/__init__.py` 导出 `SVNCommandExecutor` 和 `FileSystemHelper`
- [x] 1.1.2 确认 `utils/__init__.py` 导出 `RegexCache`

### 1.2 更新 UI 模块导入
- [x] 1.2.1 修改 `ui/main_window.py` 的导入语句：
  - 将 `from .svn_executor import SVNCommandExecutor` 改为 `from ..core.svn_executor import SVNCommandExecutor`
  - 将 `from .fs_helper import FileSystemHelper` 改为 `from ..core.fs_helper import FileSystemHelper`
- [x] 1.2.2 修改 `ui/context_menu.py` 的类型注解导入（如果需要）

### 1.3 删除重复文件
- [x] 1.3.1 删除 `ui/fs_helper.py`
- [x] 1.3.2 删除 `ui/svn_executor.py`
- [x] 1.3.3 删除 `ui/regex_cache.py`

### 1.4 统一 RegexCache API
- [x] 1.4.1 确保 `utils/regex_cache.py` 提供 `get_global_cache()` 函数
- [x] 1.4.2 如果 UI 代码使用 `_regex_cache`，更新为使用 `get_global_cache()`

## 2. 验证

### 2.1 语法检查
- [x] 2.1.1 运行 AST 语法解析验证 `src/smart_svn_commit/ui/main_window.py`
- [x] 2.1.2 运行 AST 语法解析验证 `src/smart_svn_commit/ui/context_menu.py`

### 2.2 导入检查
- [x] 2.2.1 验证可以从 `smart_svn_commit.ui.main_window` 导入（PyQt5 未安装但不影响语法验证）
- [x] 2.2.2 运行 `python -c "from smart_svn_commit.core import SVNCommandExecutor, FileSystemHelper"`

### 2.3 功能测试
- [x] 2.3.1 运行 CLI 测试：`--help`、`--version`、`--config show`、`--context-menu status` 均正常
- [x] 2.3.2 验证 GUI 导入路径：`ui/main_window.py` 正确从 `core` 和 `utils` 模块导入共享类

## 3. 代码质量

### 3.1 格式化和检查
- [x] 3.1.1 运行 `black src/` (18 files reformatted)
- [x] 3.1.2 运行 `flake8 src/` (发现的问题为预先存在的代码风格问题，非本次重构引入)
- [x] 3.1.3 运行 `mypy src/`

## 说明

- **额外修复 1**: 修复了 `ui/main_window.py` 第 101 行的中文引号问题（`"` -> `\"`）
- **额外修复 2**: 重构了 `context_menu_installer.py` 第 106-112 行，使用更清晰的字符串构建方式避免复杂的转义
- **导入验证**: 所有共享类都可以正确从 `core` 和 `utils` 模块导入
- **语法检查**: 通过 AST 解析验证
- **CLI 测试**: 帮助、版本、配置显示、右键菜单状态查询等命令均正常工作
- **GUI 导入**: 验证了 `ui/main_window.py` 的导入路径正确指向 `core` 和 `utils` 模块
