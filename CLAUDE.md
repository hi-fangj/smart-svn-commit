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

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Smart SVN Commit 是一个 AI 驱动的 SVN 提交助手工具，提供命令行接口（CLI）和可选的 PyQt5 GUI 界面。核心功能是自动生成符合 Conventional Commits 规范的提交消息，并集成 TortoiseSVN。

## 开发命令

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/

# 代码检查
flake8 src/

# 类型检查
mypy src/

# 构建发布包
python -m build

# 安装本地可编辑版本
pip install -e .

# 安装完整版（包含 AI 支持）
pip install -e ".[ai]"
```

## 代码架构

项目采用分层架构，主要分为以下几个模块：

### 核心模块 (`core/`)
- `config.py` - 配置管理，支持项目级（`.smart-svn-commit.json`）和用户级配置
- `parser.py` - SVN 状态输出解析器
- `commit.py` - SVN 提交执行器
- `svn_executor.py` - SVN 命令执行器，封装 diff/log/blame/revert/add/delete 等操作
- `fs_helper.py` - 文件系统辅助工具

### AI 模块 (`ai/`)
- `factory.py` - 提交消息生成工厂，协调 AI 和降级方案
- `generator.py` - 使用 OpenAI API 生成提交消息
- `fallback.py` - 基于关键词的降级生成方案
- `diff.py` - 获取文件 SVN diff 内容

### 工具模块 (`utils/`)
- `filters.py` - 文件过滤工具，支持通配符和忽略模式
- `regex_cache.py` - 正则表达式缓存

### 入口点
- `cli.py` - 命令行入口，处理参数解析和流程协调
- `__main__.py` - Python 模块执行入口

## 重要设计决策

### 配置加载优先级
1. 当前工作目录：`.smart-svn-commit.json`
2. 用户配置目录：
   - Windows: `%APPDATA%\smart-svn-commit\config.json`
   - Linux/Mac: `~/.config/smart-svn-commit/config.json`
3. 包内默认配置（`config/default_config.json`）

### 提交消息生成策略
1. 优先使用 AI API（如果已配置）
2. AI 失败时降级到关键词匹配
3. 默认返回 `chore: 提交变更`

### UI 可选设计
GUI 功能（PyQt5）是可选的，通过 `try/except ImportError` 处理。如果未安装 PyQt5，CLI 仍可正常运行（`--skip-ui` 模式）。

### SVN 操作集成
- Windows 下优先使用 TortoiseProc（TortoiseSVN）
- 回退到命令行 `svn` 工具
- 使用临时文件处理 `svn commit --targets`

## 依赖管理

### 必需依赖
- `PyQt5>=5.15.0` - GUI 界面（可选但推荐）

### 可选依赖
- `openai>=1.0.0` - AI 提交消息生成

### 开发依赖
- `pytest` / `pytest-qt` - 测试框架
- `black` - 代码格式化（line-length: 100）
- `flake8` - 代码检查
- `mypy` - 类型检查
- `pyinstaller` - Windows 可执行文件打包

## CI/CD

### GitHub Actions 自动化发布

项目使用 GitHub Actions 自动化构建 Windows 可执行文件并发布到 GitHub Releases。

**触发方式**：
- 推送以 `v` 开头的 Git tag（如 `v1.0.0`）
- 在 GitHub 上创建 Release

**构建配置**：
- 运行环境：`windows-latest`
- Python 版本：3.11
- 打包工具：PyInstaller（单文件模式，`--onefile --windowed`）
- 产物命名：`smart-svn-commit-v<version>-win.exe`

**本地测试打包**：
```bash
# 安装开发依赖（包含 PyInstaller）
pip install -e ".[dev]"

# 执行打包（在项目根目录）
pyinstaller ^
  --onefile ^
  --windowed ^
  --name smart-svn-commit ^
  --add-data "src/smart_svn_commit/config/*.json;smart_svn_commit/config" ^
  --hidden-import PyQt5.QtWidgets ^
  --hidden-import PyQt5.QtCore ^
  --hidden-import PyQt5.QtGui ^
  src/smart_svn_commit/cli.py
```

生成的 exe 文件位于 `dist/smart-svn-commit.exe`。

## Conventional Commits 规范

项目使用 Conventional Commits 格式：`<type>(<scope>): <description>`

支持的类型（type）：feat, fix, docs, style, refactor, perf, test, chore, build

支持的范围（scope）：guild, battle, chat, player, ui, network, config, art, audio

## SVN 状态码

解析器支持以下 SVN 状态码：M, A, D, ?, !, C, R, ~, S

## 命令行入口点

安装后注册两个命令：
- `smart-svn-commit` - 完整命令
- `ssc` - 短命令别名

## Windows 特殊处理

- PowerShell 下使用 `;` 分隔命令而非 `&&`
- 临时文件使用 `delete=False` 参数以确保 SVN 可以读取
- 中文路径需用引号包裹
