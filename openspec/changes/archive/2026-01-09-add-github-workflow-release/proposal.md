# 变更：添加 GitHub Actions 自动化发布工作流

## 为什么

当前项目缺少自动化构建和发布流程，用户需要手动安装 Python 环境和依赖才能使用 Smart SVN Commit。通过添加 GitHub Actions 工作流，可以在发布时自动构建 Windows 可执行文件（exe），为用户提供开箱即用的安装包，降低使用门槛。

## 变更内容

- 添加 GitHub Actions 工作流配置，用于自动化构建 Windows 平台的可执行文件
- 使用 PyInstaller 将项目打包为单文件 exe，包含所有依赖（PyQt5 和 OpenAI）
- 支持两种触发方式：
  - 推送以 `v` 开头的 Git tag（如 `v1.0.0`）
  - 在 GitHub 上创建 Release
- 自动将构建产物上传到 Release，供用户下载
- 生成可执行文件名为 `smart-svn-commit.exe`，包含完整功能
- 构建过程支持多版本 Python（3.8-3.12）测试

## 影响

- **受影响规范**：
  - `ci-cd` - 新增 CI/CD 相关规范
- **受影响代码**：
  - 新增 `.github/workflows/release.yml` - GitHub Actions 工作流配置
  - 新增 `build.spec` 或 `pyinstaller.config` - PyInstaller 打包配置
- **新增依赖**：
  - `pyinstaller` - 开发依赖，用于构建可执行文件
- **用户影响**：
  - 用户可直接从 GitHub Release 下载 exe 文件使用
  - 无需安装 Python 和依赖，降低使用门槛
  - 文件体积预计 50-100MB（单文件打包包含 PyQt5）
