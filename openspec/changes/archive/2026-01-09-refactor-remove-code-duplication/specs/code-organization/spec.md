# 代码组织规范

本规范定义 Smart SVN Commit 项目的模块结构和代码共享规则。

## 新增需求

### 需求：模块职责分离

项目必须采用分层架构，每个模块具有清晰的单一职责。

#### 场景：模块职责定义
- **给定** 项目采用分层架构
- **那么** 必须遵守以下模块职责划分：

| 模块 | 职责 | 可导出内容 |
|------|------|-----------|
| `core/` | 核心业务逻辑，SVN 操作，文件系统操作 | `SVNCommandExecutor`, `FileSystemHelper`, 配置管理，状态解析，提交执行 |
| `ai/` | AI 提交消息生成 | `generate_commit_message`, 相关工厂和降级方案 |
| `utils/` | 通用工具类 | `RegexCache`, `apply_ignore_patterns` |
| `ui/` | PyQt5 GUI 界面 | GUI 组件，必须从 `core/` 和 `utils/` 导入共享类 |
| `windows/` | Windows 平台特定功能 | 注册表操作，右键菜单安装 |

### 需求：禁止代码重复

共享工具类必须在唯一位置定义，其他模块通过导入使用。

#### 场景：共享类定义位置
- **当** 需要定义可在多个模块中使用的工具类
- **那么** 必须遵循以下放置规则：

| 共享类 | 定义位置 |
|--------|----------|
| `FileSystemHelper` | `core/fs_helper.py` |
| `SVNCommandExecutor` | `core/svn_executor.py` |
| `RegexCache` | `utils/regex_cache.py` |
| SVN 状态解析器 | `core/parser.py` |
| 配置管理 | `core/config.py` |
| 提交执行器 | `core/commit.py` |
| 文件过滤器 | `utils/filters.py` |

#### 场景：UI 模块导入共享类
- **当** UI 模块需要使用共享工具类
- **那么** 必须从 `core/` 或 `utils/` 导入，不得在 `ui/` 内重复定义
- **示例**：
  ```python
  # 正确
  from ..core.svn_executor import SVNCommandExecutor
  from ..core.fs_helper import FileSystemHelper
  from ..utils.regex_cache import get_global_cache

  # 错误 - 禁止
  from .svn_executor import SVNCommandExecutor  # ui/ 内不应有此文件
  ```

### 需求：模块导出规范

每个模块的 `__init__.py` 必须明确导出其公共 API。

#### 场景：core 模块导出
- **给定** `core/__init__.py` 文件存在
- **那么** 必须导出以下公共类：
  - `SVNCommandExecutor`
  - `FileSystemHelper`
  - `load_config`
  - `save_config`
  - `init_config`
  - `parse_svn_status`
  - `execute_svn_commit`
  - `run_svn_status`

#### 场景：utils 模块导出
- **给定** `utils/__init__.py` 文件存在
- **那么** 必须导出以下公共类和函数：
  - `RegexCache`
  - `get_global_cache`（如果存在）
  - `apply_ignore_patterns`

### 需求：正则表达式缓存统一

`RegexCache` 类必须在 `utils/regex_cache.py` 中统一定义，提供全局单例访问。

#### 场景：获取全局缓存实例
- **当** 任何模块需要使用正则表达式缓存
- **那么** 必须通过 `get_global_cache()` 函数获取全局单例实例
- **示例**：
  ```python
  from smart_svn_commit.utils.regex_cache import get_global_cache

  cache = get_global_cache()
  pattern = cache.get(r'\.py$')
  ```
