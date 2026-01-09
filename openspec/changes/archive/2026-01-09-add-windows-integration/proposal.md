# 提案：Windows 右键菜单集成与代码整合

## 概述

本提案旨在将现有的 `svn_commit.py` 脚本整合到项目结构中，并添加 Windows 右键菜单集成功能。

## 为什么

当前项目存在以下问题：

1. **代码分散** - `svn_commit.py` 包含完整的 GUI 实现，但未整合到项目模块结构中
2. **缺少 Windows 集成** - 没有右键菜单和安装程序
3. **未使用配置** - `splitterRatio` 窗口比例保存功能实际未被使用

## 变更内容

### 目标

1. 将 `svn_commit.py` 拆分重构为 `src/smart_svn_commit/ui/` 模块
2. 添加 Windows 右键菜单集成（仅 SVN 工作副本显示）
3. 创建 NSIS 安装程序，自动注册右键菜单
4. 移除 `splitterRatio` 窗口比例保存功能
5. 确认项目级配置（`.smart-svn-commit.json`）正常工作

**非目标**：
- 不修改 GUI 核心功能逻辑
- 不支持跨平台右键菜单（仅 Windows）

## 影响范围

### 新增模块

- `src/smart_svn_commit/ui/` - GUI 模块（从 svn_commit.py 拆分）
  - `main_window.py` - 主窗口和 `show_quick_pick()` 函数
  - `file_list_widget.py` - `FileListWidget` 类
  - `svn_executor.py` - `SVNCommandExecutor` 类
  - `fs_helper.py` - `FileSystemHelper` 类
  - `context_menu.py` - 右键菜单构建器
  - `commit_message.py` - 提交消息生成

- `src/smart_svn_commit/windows/` - Windows 平台特定功能
  - `registry.py` - 注册表操作
  - `context_menu_installer.py` - 右键菜单注册/卸载

- `installer/` - NSIS 安装程序
  - `installer.nsi` - NSIS 脚本

### 修改文件

- `src/smart_svn_commit/cli.py` - 添加右键菜单启动参数
- `src/smart_svn_commit/config/default_config.json` - 移除 `ui.splitterRatio`
- `.github/workflows/release.yml` - 添加 NSIS 打包步骤

### 删除文件

- `src/smart_svn_commit/svn_commit.py` - 代码拆分后删除

### 新增命令行参数

- `ssc --file <path>` - 打开 GUI 并显示指定文件
- `ssc --dir <path>` - 打开 GUI 并显示目录下变更文件
- `ssc --context-menu install` - 手动注册右键菜单
- `ssc --context-menu uninstall` - 手动卸载右键菜单

## 技术方案

### 1. 代码拆分

将 `svn_commit.py` (1896 行) 按功能拆分：

| 原代码 | 目标模块 |
|--------|----------|
| `show_quick_pick()` 函数 | `ui/main_window.py` |
| `FileListWidget` 类 | `ui/file_list_widget.py` |
| `SVNCommandExecutor` 类 | `ui/svn_executor.py` |
| `FileSystemHelper` 类 | `ui/fs_helper.py` |
| `ContextMenuBuilder` 类 | `ui/context_menu.py` |
| `generate_commit_message*()` 函数 | `ui/commit_message.py` |

### 2. 右键菜单注册

**检测 SVN 工作副本的方案**：

使用动态注册表 + Python 检测脚本：

```
HKEY_CURRENT_USER\SOFTWARE\Classes\Directory\Background\shell\smart-svn-commit\command
@="pythonw.exe -c \"import sys; sys.path.insert(0, 'INSTALL_DIR'); from smart_svn_commit.windows.context_menu_installer import handle_context_menu; handle_context_menu('%V')\""
```

检测脚本逻辑：
1. 检查目录是否包含 `.svn` 子目录
2. 如果是 SVN 工作副本，启动 GUI
3. 如果不是，静默退出（不显示菜单项）

### 3. NSIS 安装程序

```nsis
; 安装流程
1. 复制文件到 Program Files
2. 执行 smart-svn-commit.exe --context-menu install
3. 创建桌面快捷方式（可选）
4. 添加到系统 PATH

; 卸载流程
1. 执行 smart-svn-commit.exe --context-menu uninstall
2. 删除程序文件
```

### 4. 移除窗口比例保存

删除以下代码：

| 位置 | 代码 |
|------|------|
| `show_quick_pick()` 第 1279-1286 行 | 加载 `splitterRatio` 配置 |
| `show_quick_pick()` 第 1671-1683 行 | 保存 `splitterRatio` 配置 |
| `default_config.json` | `ui.splitterRatio` 字段 |

## 风险与依赖

### 风险

1. **代码拆分风险** - 1896 行代码拆分可能引入导入错误
2. **PyInstaller 打包** - 需要确保所有依赖正确打包
3. **NSIS 学习曲线** - 需要编写 NSIS 脚本

### 依赖

- PyQt5 >= 5.15.0
- Windows 10/11
- NSIS（用于构建安装程序）

## 实施计划

详见 `tasks.md`。

## 验收标准

1. `svn_commit.py` 成功拆分为 `ui/` 模块
2. `ssc` 命令可以正常启动 GUI
3. NSIS 安装程序可以成功安装和卸载
4. 安装后在 SVN 项目中右键可以看到 "Smart SVN Commit" 选项
5. 非 SVN 目录中不显示右键菜单选项
6. 点击目录显示所有变更文件，点击文件只显示该文件
7. 默认配置中不包含 `ui.splitterRatio`
8. 项目级配置 `.smart-svn-commit.json` 可以覆盖用户级配置
