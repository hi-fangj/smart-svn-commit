# ci-cd Specification

## Purpose
TBD - created by archiving change add-github-workflow-release. Update Purpose after archive.
## 需求
### 需求：GitHub Actions 自动化发布工作流

项目必须提供 GitHub Actions 工作流，用于自动化构建和发布 Windows 平台的可执行文件。

#### 场景：通过 Git Tag 触发构建

- **当** 开发者推送以 `v` 开头的 Git tag（如 `v1.0.0`）到 GitHub
- **那么** GitHub Actions 应自动触发构建流程
- **并且** 构建成功后生成 Windows 可执行文件
- **并且** 将可执行文件上传到对应的 Release

#### 场景：通过 Release 创建触发构建

- **当** 用户在 GitHub 上创建新的 Release
- **那么** GitHub Actions 应自动触发构建流程
- **并且** 构建成功后生成 Windows 可执行文件
- **并且** 将可执行文件上传到该 Release

#### 场景：构建成功上传产物

- **当** GitHub Actions 工作流成功构建可执行文件
- **那么** 应将 exe 文件作为构建产物上传
- **并且** 文件名应包含版本号（如 `smart-svn-commit-v1.0.0-win.exe`）
- **并且** 用户可从 Release 页面直接下载

### 需求：PyInstaller 打包配置

项目必须使用 PyInstaller 将 Python 代码打包为 Windows 可执行文件。

#### 场景：单文件打包

- **当** 执行 PyInstaller 打包命令
- **那么** 必须使用 `--onefile` 模式生成单个 exe 文件
- **并且** 所有依赖（Python 运行时、库、资源）都打包在单个文件中
- **并且** 用户可以直接运行该 exe，无需安装 Python

#### 场景：GUI 模式打包

- **当** 执行 PyInstaller 打包命令
- **那么** 必须使用 `--windowed` 模式隐藏控制台窗口
- **并且** 应用以 GUI 方式启动，不显示命令行窗口

#### 场景：配置文件打包

- **当** 执行 PyInstaller 打包命令
- **那么** 必须将 `src/smart_svn_commit/config/default_config.json` 打包进 exe
- **并且** 应用启动时能正确加载默认配置
- **并且** 用户级和项目级配置文件优先级仍然生效

#### 场景：PyQt5 依赖打包

- **当** 执行 PyInstaller 打包命令
- **那么** 必须正确打包所有 PyQt5 相关模块
- **并且** 必须使用 `--hidden-import` 参数确保以下模块被包含：
  - `PyQt5.QtWidgets`
  - `PyQt5.QtCore`
  - `PyQt5.QtGui`
- **并且** GUI 界面能正常显示和交互

#### 场景：AI 依赖打包

- **当** 执行 PyInstaller 打包命令
- **那么** 必须包含 OpenAI 库及其依赖
- **并且** 用户配置 API Key 后可使用 AI 功能
- **并且** AI 不可用时应能正常降级到关键词匹配方案

### 需求：开发依赖管理

项目必须将 PyInstaller 作为开发依赖进行管理。

#### 场景：安装开发依赖

- **当** 开发者执行 `pip install -e ".[dev]"`
- **那么** 必须自动安装 PyInstaller
- **并且** 开发者可以在本地使用 `pyinstaller` 命令测试打包

### 需求：构建产物命名规范

生成的可执行文件必须遵循统一的命名规范。

#### 场景：标准命名格式

- **当** GitHub Actions 工作流生成可执行文件
- **那么** 文件名必须遵循格式：`smart-svn-commit-v<version>-win.exe`
- **例如**：`smart-svn-commit-v1.0.0-win.exe`
- **并且** 版本号应从 Git tag 或项目版本中获取

### 需求：用户安装方式

项目必须支持多种安装方式，包括预编译的可执行文件。

#### 场景：从 Release 下载 exe

- **当** 用户访问 GitHub Release 页面
- **那么** 应找到 Windows 可执行文件下载链接
- **并且** 下载后可直接运行，无需安装 Python
- **并且** 首次运行时应能正常初始化配置

#### 场景：系统要求说明

- **当** 用户查看 README.md
- **那么** 必须明确说明使用 exe 文件的系统要求
- **并且** 必须说明仍需安装 SVN 命令行工具或 TortoiseSVN
- **并且** 必须说明 exe 文件已包含 Python 环境和所有依赖

