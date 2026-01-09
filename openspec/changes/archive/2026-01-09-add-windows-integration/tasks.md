# 任务清单：Windows 集成与代码整合

## 阶段 1：代码拆分与重构

### 1.1 创建 UI 模块结构
- [x] 创建 `src/smart_svn_commit/ui/` 目录
- [x] 创建 `ui/__init__.py`，导出 `show_quick_pick` 函数
- [x] 创建 `ui/file_list_widget.py`
- [x] 创建 `ui/svn_executor.py`
- [x] 创建 `ui/fs_helper.py`
- [x] 创建 `ui/context_menu.py`
- [x] 创建 `ui/commit_message.py`
- [x] 创建 `ui/main_window.py`

### 1.2 拆分 FileListWidget 类
- [x] 将 `FileListWidget` 类移至 `ui/file_list_widget.py`
- [x] 提取 `_RegexCache` 类到 `ui/regex_cache.py`
- [x] 提取 `UIStyles` 常量类到 `ui/styles.py`

### 1.3 拆分 SVN 执行器和文件系统辅助
- [x] 将 `SVNCommandExecutor` 类移至 `ui/svn_executor.py`
- [x] 将 `FileSystemHelper` 类移至 `ui/fs_helper.py`

### 1.4 拆分上下文菜单构建器
- [x] 将 `ContextMenuBuilder` 类移至 `ui/context_menu.py`
- [x] 提取菜单常量到 `ui/menu_constants.py`

### 1.5 拆分提交消息生成
- [x] 将 `generate_commit_message_with_ai()` 移至 `ui/commit_message.py`
- [x] 将 `_generate_commit_message_by_keywords()` 移至 `ui/commit_message.py`
- [x] 将 `get_file_diff()` 移至 `ui/commit_message.py`

### 1.6 拆分主窗口
- [x] 将 `show_quick_pick()` 函数移至 `ui/main_window.py`
- [x] **移除窗口比例保存代码**（第 1279-1286 行和 1671-1683 行）

### 1.7 更新 CLI 入口
- [x] 修改 `cli.py`，从 `ui.main_window` 导入 `show_quick_pick`
- [x] 添加 `--file <path>` 参数
- [x] 添加 `--dir <path>` 参数

### 1.8 清理与验证
- [x] 删除 `src/smart_svn_commit/svn_commit.py`

---

## 阶段 2：移除窗口比例保存

### 2.1 移除配置
- [x] 从 `src/smart_svn_commit/config/default_config.json` 移除 `ui.splitterRatio`

---

## 阶段 3：Windows 右键菜单集成

### 3.1 创建 Windows 模块
- [x] 创建 `src/smart_svn_commit/windows/` 目录
- [x] 创建 `windows/__init__.py`
- [x] 创建 `windows/registry.py` - 注册表操作函数
- [x] 创建 `windows/context_menu_installer.py` - 右键菜单安装

### 3.2 实现 SVN 工作副本检测
- [x] 实现 `is_svn_working_copy(path)` 函数
- [x] 实现 `handle_context_menu(path)` 函数

### 3.3 实现注册表操作
- [x] 实现 `register_context_menu()` 函数
- [x] 实现 `unregister_context_menu()` 函数

### 3.4 添加 CLI 命令
- [x] 添加 `--context-menu install` 命令
- [x] 添加 `--context-menu uninstall` 命令
- [x] 添加 `--context-menu status` 命令

---

## 阶段 4：NSIS 安装程序

### 4.1 创建安装程序目录
- [x] 创建 `installer/` 目录
- [x] 创建 `installer/installer.nsi`

### 4.2 编写 NSIS 脚本
- [x] 定义安装目录和文件
- [x] 编写安装步骤（复制文件、注册菜单）
- [x] 编写卸载步骤（注销菜单、删除文件）
- [x] 添加创建桌面快捷方式选项

---

## 阶段 5：CI/CD 集成

### 5.1 更新 GitHub Actions
- [x] 添加 NSIS 下载和配置步骤
- [x] 添加 PyInstaller 打包步骤
- [x] 添加 NSIS 构建步骤
- [x] 上传安装程序到 Release

---

## 阶段 6：文档与验收

### 6.1 更新文档
- [x] 更新 README.md，添加安装程序下载说明
- [x] 更新 CLAUDE.md，记录新增模块

## 依赖关系

```
阶段 1 (代码拆分)
    ↓
阶段 2 (移除窗口比例)
    ↓
阶段 3 (右键菜单) ← 并行 → 阶段 4 (NSIS 安装程序)
    ↓
阶段 5 (CI/CD)
    ↓
阶段 6 (验收)
```

## 可并行任务

- **1.2 - 1.6** 可并行进行（各自拆分独立模块）
- **阶段 2** 可与 **阶段 3** 部分并行
- **阶段 3** 和 **阶段 4** 可部分并行
