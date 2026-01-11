<!-- OPENSPEC:START -->
# OpenSpec 使用说明

这些说明适用于在此项目中工作的AI助手。

## 语言偏好设置

**默认使用中文**：除非明确说明使用英文，否则所有输出都应使用中文，包括：
- 文档内容
- 代码注释
- 提交信息
- 规范说明

## 工作流程

当请求满足以下条件时，始终打开`@/openspec/AGENTS.md`：
- 提及规划或提案（如提案、规范、变更、计划等词语）
- 引入新功能、重大变更、架构变更或大型性能/安全工作时
- 听起来不明确，需要在编码前了解权威规范时

使用`@/openspec/AGENTS.md`了解：
- 如何创建和应用变更提案
- 规范格式和约定
- 项目结构和指南

保持此托管块，以便'openspec-cn update'可以刷新说明。

<!-- OPENSPEC:END -->

# AI Agent 指南

本指南为在此代码库中工作的 AI 编码代理提供开发规范和最佳实践。

## 构建与测试命令

```bash
pip install -e ".[dev]"
pytest
pytest tests/test_parser.py::test_parse_content_change -v
pytest tests/test_parser.py -v
black src/
flake8 src/
mypy src/
python -m build
```

## 代码风格指南

**格式化**：Black，最大行长度 100 字符，目标 Python 版本 3.8+

### 导入顺序、类型注解和命名约定

```python
# 标准库
import json, sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 第三方库（带 try/except 处理可选依赖）
try:
    from openai import OpenAI as OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget

# 本地模块（相对导入）
from ..core.config import load_config
from .constants import CHECKBOX_COLUMN

# 常量：UPPER_CASE，类：PascalCase，函数：snake_case，私有：_prefix
PROJECT_CONFIG_NAME = ".smart-svn-commit.json"
DEFAULT_MESSAGE = "chore: 提交变更"

class ConfigManager:
    """配置管理器 - 单例模式，支持配置缓存"""

def parse_svn_status(status_output: str) -> List[Tuple[str, str]]:
    """解析 SVN 状态输出，提取文件路径和状态"""

def _load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    """从文件加载 JSON 配置（内部函数）"""
```

### 错误处理、文档字符串和测试风格

```python
try:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
except (json.JSONDecodeError, IOError) as e:
    print(f"警告: 无法读取配置文件 {path}: {e}", file=sys.stderr)
    return None

result = subprocess.run(["svn", "status"], capture_output=True, text=True,
                        check=False, encoding="utf-8", errors="ignore")
if result.returncode == 0:
    return parse_svn_status(result.stdout)

try:
    result = subprocess.run(...)
    return result
finally:
    try:
        os.unlink(temp_file)
    except (FileNotFoundError, PermissionError, OSError):
        pass

def parse_svn_status(status_output: str) -> List[Tuple[str, str]]:
    """
    解析 SVN 状态输出，提取文件路径和状态

    Args:
        status_output: svn status 命令的原始输出

    Returns:
        (状态, 文件路径) 元组列表
    """
    pass

def test_parse_content_change():
    """测试纯内容变动解析"""
    output = "M       file.txt
"
    result = parse_svn_status(output)
    assert result == [("M", "file.txt")]
```

### 可选依赖、平台特定代码和 Qt UI 风格

```python
try:
    from smart_svn_commit.ui.main_window import show_quick_pick
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False

if not UI_AVAILABLE:
    print("错误: PyQt5 未安装，无法使用 GUI", file=sys.stderr)
    sys.exit(1)

if sys.platform == "win32":
    from smart_svn_commit.windows import register_context_menu
    WINDOWS_AVAILABLE = True
else:
    WINDOWS_AVAILABLE = False

from .constants import CHECKBOX_COLUMN, PATH_COLUMN

class FileListWidget:
    """带复选框的文件列表控件"""

    def _setup_tree(self) -> None:
        """初始化树控件配置（内部方法）"""
        self.tree.setHeaderLabels(["", "文件路径"])
        self.tree.setColumnWidth(CHECKBOX_COLUMN, 30)

    def add_item(self, status: str, path: str) -> None:
        """添加文件项"""
        tree_item = QTreeWidgetItem()
        tree_item.setFlags(tree_item.flags() | Qt.ItemIsUserCheckable)
        tree_item.setCheckState(CHECKBOX_COLUMN, Qt.Unchecked)
        tree_item.setText(PATH_COLUMN, f"[{status}] {path}")
        self.tree.addTopLevelItem(tree_item)
```

### 配置文件处理和模块组织

```python
from pathlib import Path

def get_config_path() -> Path:
    """获取配置文件路径"""
    cwd_config = Path.cwd() / PROJECT_CONFIG_NAME
    if cwd_config.exists():
        return cwd_config
    config_dir = Path.home() / ".config" / USER_CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / USER_CONFIG_NAME

with open(path, "r", encoding="utf-8") as f:
    return json.load(f)

with open(path, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

# 模块组织：src/smart_svn_commit/ (cli.py, core/, ai/, utils/, ui/, windows/)
```

## 重要约定

1. **中文注释和文档**：除非用户明确要求英文，否则使用中文
2. **无注释**：代码实现不添加注释，除非用户明确要求
3. **类型注解**：所有公共 API 必须包含类型注解
4. **错误处理**：关键路径必须有错误处理
5. **可选依赖**：使用 try/except ImportError 处理可选依赖
6. **临时文件**：Windows 下使用 delete=False 参数确保 SVN 可以读取
7. **中文路径**：Windows 下路径用引号包裹
8. **幂等性**：配置加载等操作支持缓存和重新加载
