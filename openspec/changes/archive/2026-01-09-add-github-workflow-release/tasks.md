# 实施任务清单

## 1. 项目配置准备
- [x] 1.1 更新 `pyproject.toml`，添加 `pyinstaller` 到开发依赖
- [x] 1.2 创建 PyInstaller 配置文件（`pyinstaller.config` 或使用命令行参数）

## 2. GitHub Actions 工作流实现
- [x] 2.1 创建 `.github/workflows/` 目录
- [x] 2.2 编写 `release.yml` 工作流配置文件
- [x] 2.3 配置工作流触发条件（Git tag push 和 Release 创建）
- [x] 2.4 实现构建步骤：检出代码、设置 Python、安装依赖
- [x] 2.5 实现 PyInstaller 打包步骤（单文件模式）
- [x] 2.6 配置构建产物上传到 Release

## 3. PyInstaller 配置优化
- [x] 3.1 配置数据文件打包（确保 `config/default_config.json` 被包含）
- [x] 3.2 配置隐藏导入（PyQt5 模块）
- [x] 3.3 配置图标（可选，如果有项目图标）
- [x] 3.4 配置控制台选项（GUI 模式隐藏控制台窗口）

## 4. 验证与测试
- [x] 4.1 本地测试 PyInstaller 打包命令
- [x] 4.2 验证生成的 exe 文件能正常启动
- [x] 4.3 验证 GUI 界面正常显示
- [x] 4.4 验证 SVN 命令执行功能
- [x] 4.5 验证配置文件加载
- [x] 4.6 测试 AI 功能（如已配置 API Key）

## 5. 文档更新
- [x] 5.1 更新 README.md，添加 Release 下载说明
- [x] 5.2 在 README 中添加 exe 使用注意事项（需要安装 SVN/TortoiseSVN）
- [x] 5.3 更新 CLAUDE.md，记录新的 CI/CD 流程

## 依赖关系
- 任务 1 和 2 可以并行
- 任务 3 依赖于任务 1
- 任务 4 依赖于任务 2 和 3
- 任务 5 可以在任务 4 开始后并行

## 可验证指标
- 工作流运行成功，生成 exe 文件
- Release 页面包含可下载的 exe 文件
- exe 文件可在 Windows 上独立运行（无需 Python 环境）
- 文件大小在合理范围内（50-150MB）
