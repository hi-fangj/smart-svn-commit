# Smart SVN Commit

> AI 驱动的 SVN 提交助手，提供友好的 PyQt5 GUI 界面

Smart SVN Commit 是一个强大的 SVN 提交工具，提供图形化界面选择文件、智能生成符合 Conventional Commits 规范的提交消息，并完美集成 TortoiseSVN。

## 特性

- **友好界面**: 基于 PyQt5 的现代化 GUI，支持文件选择、搜索、排序
- **AI 生成**: 支持使用 OpenAI 兼容 API 自动生成提交消息
- **TortoiseSVN 集成**: Windows 下完美集成 TortoiseSVN 操作
- **智能过滤**: 支持通配符搜索和自定义忽略模式
- **快捷键**: 支持键盘快捷操作（Enter 确认、ESC 取消、F5 刷新）
- **灵活配置**: 支持项目级和用户级配置文件

## 安装

### 基础安装

```bash
pip install smart-svn-commit
```

### 完整安装（包含 AI 支持）

```bash
pip install smart-svn-commit[ai]
```

## 快速开始

### 基本用法

```bash
# 自动检测 SVN 状态并显示 GUI
smart-svn-commit

# 使用短命令别名
ssc

# 指定文件列表
smart-svn-commit --files="file1.cs,file2.cs"

# 从 SVN 管道输入
svn status | smart-svn-commit --status
```

### 配置 AI

```bash
# 初始化配置文件
smart-svn-commit --config init

# 编辑配置文件
smart-svn-commit --config edit
```

在配置文件中设置您的 AI API：

```json
{
  "aiApi": {
    "enabled": true,
    "baseUrl": "https://api.openai.com/v1",
    "apiKey": "your-api-key-here",
    "model": "gpt-3.5-turbo"
  }
}
```

### 跳过 GUI（自动化）

```bash
# 自动生成提交消息，跳过 GUI
smart-svn-commit --files="file1.cs,file2.cs" --skip-ui
```

## GUI 功能

### 文件选择

- **复选框点击**: 确认选择/取消文件
- **路径点击**: 高亮选中文件（蓝色背景）
- **Shift + 路径点击**: 范围选择（两次点击确定范围）

### 搜索过滤

- **普通文本**: 大小写不敏感的包含匹配
- **通配符**: `*.cs` 匹配所有 .cs 文件，`Test*.cs` 匹配以 Test 开头的 .cs 文件

### 排序功能

- **按路径**: 按文件路径字母顺序排序
- **按后缀**: 按文件扩展名分组排序（无后缀排在最后）
- **按状态**: 按 SVN 状态码（M/A/D/?）排序

### 快捷键

- `Enter`: 确认提交
- `ESC`: 取消
- `F5`: 刷新 SVN 状态
- `双击路径`: 打开 SVN diff 对比工具
- `右键路径`: 显示 SVN 操作菜单

### 右键菜单

根据文件状态动态显示菜单选项：

- **查看差异** (diff): 打开 SVN diff 工具
- **查看日志** (log): 查看文件提交历史
- **查看注释** (blame): 查看每行代码的修改信息
- **还原** (revert): 还原文件到未修改状态
- **添加** (add): 添加新文件到版本控制
- **删除** (delete): 从版本控制中删除文件
- **打开文件**: 使用系统默认程序打开
- **打开所在目录**: 在文件管理器中打开并选中文件

## 配置文件

### 配置文件位置

配置文件查找优先级：

1. 当前工作目录: `.smart-svn-commit.json`
2. 用户配置目录:
   - Windows: `%APPDATA%\smart-svn-commit\config.json`
   - Linux/Mac: `~/.config/smart-svn-commit/config.json`

### 配置选项

```json
{
  "ignorePatterns": [
    "Library/",
    "Temp/",
    ".vs/",
    "obj/",
    "UserSettings/"
  ],
  "commitMessage": {
    "format": "conventional",
    "language": "zh",
    "types": ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "build"],
    "scopes": ["guild", "battle", "chat", "player", "ui", "network", "config", "art", "audio"]
  },
  "ui": {
    "splitterRatio": [30, 70]
  },
  "aiApi": {
    "enabled": false,
    "baseUrl": "",
    "apiKey": "",
    "model": "gpt-3.5-turbo",
    "prompts": {
      "system": "系统提示词...",
      "user": "用户提示词模板..."
    }
  }
}
```

## 命令行参数

```
usage: smart-svn-commit [-h] [--version] [--files FILES] [--status] [--skip-ui]
                        [--ignore IGNORE | --no-ignore]
                        [--config {init,edit,show}]

options:
  -h, --help            显示帮助信息
  --version             显示版本号
  --files FILES         逗号分隔的文件列表
  --status              从 stdin 读取 SVN 状态输出
  --skip-ui             跳过 GUI，直接使用提供的文件列表
  --ignore IGNORE       逗号分隔的忽略模式（覆盖配置文件）
  --no-ignore           禁用所有忽略模式
  --config {init,edit,show}
                        配置管理操作
```

## Python API

```python
from smart_svn_commit import (
    SVNCommandExecutor,
    generate_commit_message,
    load_config,
    parse_svn_status,
)

# 执行 SVN 命令
executor = SVNCommandExecutor()
executor.diff("path/to/file.cs")
executor.log("path/to/file.cs")

# 生成提交消息
message = generate_commit_message([
    "Assets/Scripts/UI/MainPanel.cs",
    "Assets/Scripts/Model/PlayerComponent.cs"
])

# 解析 SVN 状态
status_output = """M       Assets/Scripts/File.cs
A       Assets/NewFile.cs"""
files = parse_svn_status(status_output)
```

## 系统要求

- Python 3.8+
- PyQt5 5.15+
- SVN 命令行工具（可选，用于 SVN 操作）
- TortoiseSVN（可选，Windows 下提供更好的集成体验）

## 开发

```bash
# 克隆仓库
git clone https://github.com/hi-fangj/smart-svn-commit.git
cd smart-svn-commit

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
flake8 src/

# 构建包
python -m build
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

本项目基于原有的 SVN 提交助手工具重构而来，感谢原作者的贡献。

## 链接

- [GitHub 仓库](https://github.com/hi-fangj/smart-svn-commit)
- [问题反馈](https://github.com/hi-fangj/smart-svn-commit/issues)
