# Windows 集成规范

本规范定义了 Smart SVN Commit 项目在 Windows 平台上的集成功能，包括右键菜单集成和安装程序。

## 新增需求

### 需求：GUI 模块化

项目必须将 GUI 代码模块化，拆分为独立的子模块。

#### 场景：UI 模块结构

- **当** 查看项目 `src/smart_svn_commit/ui/` 目录
- **那么** 必须包含以下模块文件：
  - `main_window.py` - 主窗口和 `show_quick_pick()` 函数
  - `file_list_widget.py` - `FileListWidget` 类
  - `svn_executor.py` - `SVNCommandExecutor` 类
  - `fs_helper.py` - `FileSystemHelper` 类
  - `context_menu.py` - 右键菜单构建器
  - `commit_message.py` - 提交消息生成
  - `constants.py` - UI 常量定义
  - `menu_constants.py` - 右键菜单常量
  - `styles.py` - UI 样式配置
  - `regex_cache.py` - 正则表达式缓存

#### 场景：Windows 模块结构

- **当** 查看项目 `src/smart_svn_commit/windows/` 目录
- **那么** 必须包含以下模块文件：
  - `registry.py` - 注册表操作辅助函数
  - `context_menu_installer.py` - 右键菜单注册/卸载

### 需求：Windows 右键菜单集成

项目必须在 Windows 平台提供右键菜单集成功能。

#### 场景：SVN 工作副本检测

- **当** 用户在任意目录右键
- **那么** 仅当目录包含 `.svn` 子目录时显示 "Smart SVN Commit" 菜单项
- **并且** 非 SVN 目录不显示该菜单项

#### 场景：右键菜单注册

- **当** 执行 `smart-svn-commit --context-menu install`
- **那么** 必须在注册表 `HKEY_CURRENT_USER\SOFTWARE\Classes\Directory\Background\shell\smart-svn-commit` 创建菜单项
- **并且** 菜单显示名称为 "Smart SVN Commit"

#### 场景：右键菜单卸载

- **当** 执行 `smart-svn-commit --context-menu uninstall`
- **那么** 必须删除注册表中的 `smart-svn-commit` 菜单项
- **并且** 右键菜单不再显示该选项

#### 场景：右键菜单启动 GUI

- **当** 用户在 SVN 工作副本目录中右键点击 "Smart SVN Commit"
- **那么** 必须启动 GUI 显示该目录下的所有变更文件
- **并且** 用户可以正常选择文件并提交

### 需求：NSIS 安装程序

项目必须提供 NSIS 安装程序用于 Windows 平台分发。

#### 场景：安装程序位置

- **当** 查看项目根目录
- **那么** 必须包含 `installer/` 目录
- **并且** 目录中包含 `installer.nsi` 脚本文件

#### 场景：安装程序功能

- **当** 用户运行 NSIS 安装程序
- **那么** 必须执行以下操作：
  - 将文件复制到 Program Files 目录
  - 注册 Windows 右键菜单
  - 创建桌面快捷方式
  - 创建开始菜单快捷方式

#### 场景：卸载程序功能

- **当** 用户运行卸载程序
- **那么** 必须执行以下操作：
  - 卸载 Windows 右键菜单
  - 删除程序文件
  - 删除快捷方式

### 需求：命令行参数扩展

项目必须支持新的命令行参数以支持 Windows 集成。

#### 场景：打开指定文件

- **当** 执行 `smart-svn-commit --file <path>`
- **那么** 必须启动 GUI 并仅显示指定文件
- **并且** 文件状态默认为 "修改"（M）

#### 场景：打开目录变更

- **当** 执行 `smart-svn-commit --dir <path>`
- **那么** 必须切换到指定目录
- **并且** 启动 GUI 显示该目录下的所有变更文件

#### 场景：右键菜单管理

- **当** 执行 `smart-svn-commit --context-menu install`
- **那么** 必须注册 Windows 右键菜单

- **当** 执行 `smart-svn-commit --context-menu uninstall`
- **那么** 必须卸载 Windows 右键菜单

- **当** 执行 `smart-svn-commit --context-menu status`
- **那么** 必须显示右键菜单注册状态
- **并且** 返回适当的退出码（0=已注册，1=未注册）

### 需求：项目级配置优先级

项目必须支持项目级配置文件覆盖用户级配置。

#### 场景：项目配置文件优先

- **当** 项目根目录存在 `.smart-svn-commit.json`
- **那么** 必须优先使用项目级配置
- **并且** 项目级配置覆盖用户级配置的对应字段

#### 场景：用户配置作为默认值

- **当** 项目根目录不存在 `.smart-svn-commit.json`
- **那么** 必须使用用户级配置
- **并且** 配置路径为：
  - Windows: `%APPDATA%\smart-svn-commit\config.json`
  - Linux/Mac: `~/.config/smart-svn-commit/config.json`

#### 场景：包内默认配置

- **当** 项目级和用户级配置都不存在
- **那么** 必须使用包内默认配置 `src/smart_svn_commit/config/default_config.json`
