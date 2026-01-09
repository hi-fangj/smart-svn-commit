# 设计文档：GitHub Actions 自动化发布工作流

## 上下文

Smart SVN Commit 是一个 Python 项目，用户需要安装 Python 3.8+、PyQt5 等依赖才能使用。这对不熟悉 Python 的用户造成了一定的使用门槛。通过提供预编译的 Windows 可执行文件，可以让用户直接下载运行，无需配置开发环境。

### 约束条件
- 项目使用 PyQt5 作为 GUI 框架，体积较大
- AI 功能依赖 OpenAI 库，用户可能需要也可能不需要
- 项目包含配置文件（`config/default_config.json`）需要正确打包
- 目标平台为 Windows（项目主要面向 Windows Unity 开发者）

### 利益相关者
- 最终用户：希望快速安装使用，不想配置 Python 环境
- 项目维护者：希望自动化发布流程，减少手动操作

## 目标 / 非目标

### 目标
- 自动化构建 Windows 可执行文件
- 支持 Git tag 和 Release 两种触发方式
- 生成单文件 exe，便于分发
- 包含完整功能（GUI 和 AI）
- 自动上传到 GitHub Release

### 非目标
- 不支持 Linux/macOS 构建（可后续扩展）
- 不提供安装程序（Installer），仅提供绿色版 exe
- 不处理自动更新功能

## 决策

### 决策 1：使用 PyInstaller 作为打包工具

**选择**：PyInstaller

**原因**：
- 成熟稳定，社区活跃，文档完善
- 支持单文件打包模式
- 对 PyQt5 支持良好
- 可通过配置文件灵活控制打包行为

**考虑的替代方案**：
- cx_Freeze：配置简单，但单文件支持不如 PyInstaller
- Nuitka：编译为 C 代码性能好，但编译时间长，配置复杂

### 决策 2：单文件打包模式

**选择**：使用 `--onefile` 模式

**原因**：
- 用户下载单个文件即可使用，体验最佳
- 便于通过 GitHub Release 分发
- 避免文件散乱，用户解压即用

**权衡**：
- 启动时间稍慢（需要解压到临时目录）
- 文件体积较大（约 50-100MB）
- 但这些权衡对于桌面工具可接受

### 决策 3：包含 AI 依赖

**选择**：在打包时包含 `openai` 库

**原因**：
- 提供完整功能，用户不需要额外安装
- 虽然 OpenAI 库体积不大（约 1-2MB），但价值高
- 用户可以选择性配置 API Key，不配置则使用降级方案

### 决策 4：触发方式

**选择**：支持 Git tag push 和 Release 创建两种方式

**原因**：
- Git tag：符合语义化版本规范，适合常规发布
- Release 创建：方便从 GitHub Web 界面手动触发
- 两者互补，提供灵活性

## 工作流设计

### 触发条件

```yaml
on:
  push:
    tags:
      - 'v*.*.*'  # 匹配 v1.0.0, v2.1.3 等
  release:
    types: [created]  # Release 创建时触发
```

### 构建步骤

1. **环境准备**
   - 检出代码
   - 设置 Python 3.11（推荐版本，兼容性好）
   - 安装依赖（包括 `[ai]` 可选依赖）

2. **打包配置**
   - 使用 PyInstaller 命令行参数或配置文件
   - 关键参数：
     - `--onefile`：单文件模式
     - `--windowed`：隐藏控制台窗口（GUI 应用）
     - `--name smart-svn-commit`：输出文件名
     - `--add-data "src/smart_svn_commit/config;config"`：包含配置文件
     - `--hidden-import PyQt5.QtWidgets`：确保 PyQt5 模块被打包

3. **产物处理**
   - 将生成的 exe 文件重命名包含版本号
   - 上传到 Release 作为构建产物

### PyInstaller 配置

使用命令行参数方式（简单直接）：

```bash
pyinstaller \
  --onefile \
  --windowed \
  --name smart-svn-commit \
  --add-data "src/smart_svn_commit/config/*.json;smart_svn_commit/config" \
  --hidden-import PyQt5.QtWidgets \
  --hidden-import PyQt5.QtCore \
  --hidden-import PyQt5.QtGui \
  src/smart_svn_commit/cli.py
```

## 风险 / 权衡

### 风险 1：文件体积过大

**风险**：PyQt5 是大型库，单文件可能达到 80-100MB

**缓解措施**：
- 接受当前大小，现代网络下载 100MB 不成问题
- 后续可考虑使用 UPX 压缩（可能引发杀软误报）
- 未来可提供"精简版"（不含 GUI）和"完整版"两个版本

### 风险 2：杀毒软件误报

**风险**：PyInstaller 打包的 exe 可能被部分杀软误报

**缓解措施**：
- 这是 PyInstaller 的已知问题，无法完全避免
- 在 README 中说明可能需要添加信任
- 考虑代码签名（需要购买证书，成本较高）

### 风险 3：构建时间较长

**风险**：PyInstaller 打包可能需要 2-5 分钟

**缓解措施**：
- 可接受范围，发布不频繁
- 使用 GitHub Actions 免费额度足够
- 可以通过缓存依赖加速构建

## 迁移计划

### 实施步骤
1. 更新 `pyproject.toml` 添加 PyInstaller 依赖
2. 创建 GitHub Actions 工作流文件
3. 本地测试打包命令，确保可执行文件正常工作
4. 提交代码，推送到 GitHub
5. 创建测试 tag 触发构建
6. 验证 Release 页面的构建产物
7. 更新 README 文档

### 回滚计划
- 如果工作流有问题，可以直接删除 `.github/workflows/release.yml`
- 如果打包产物有问题，可以删除 Release，修复后重新发布
- 不影响现有用户通过 pip 安装的方式

## 待决问题

- [ ] 是否需要添加应用图标？（需要设计图标文件）
- [ ] 是否需要代码签名以减少杀软误报？（需要购买证书，成本约 $100-500/年）
- [ ] 未来是否需要支持 Linux/macOS？（可在用户有需求时考虑）
