# 项目 上下文

## 目的

Smart SVN Commit 是一个 AI 驱动的 SVN 提交助手工具，提供命令行接口（CLI）和可选的 PyQt5 GUI 界面。核心功能是：

- **自动生成提交消息** - 使用 AI 分析变更，生成符合 Conventional Commits 规范的提交消息
- **集成 TortoiseSVN** - 在 Windows 下优先使用 TortoiseProc 执行提交操作
- **智能降级** - AI 不可用时自动降级到基于关键词的生成方案
- **灵活配置** - 支持项目级和用户级配置，自定义提交类型、范围和文件过滤规则

## 技术栈

- **Python 3.8+** - 主要开发语言
- **PyQt5 5.15+** - GUI 界面（可选依赖）
- **OpenAI API** - AI 提交消息生成（可选依赖）
- **SVN / TortoiseSVN** - 版本控制工具
- **pytest / pytest-qt** - 测试框架
- **black** - 代码格式化（line-length: 100）
- **flake8** - 代码检查
- **mypy** - 类型检查

## 项目约定

### 代码风格

- **格式化**: 使用 black，行长度限制 100 字符
- **检查**: 使用 flake8 进行代码质量检查
- **类型**: 使用 mypy 进行静态类型检查
- **语言**: 默认使用中文，所有输出（文档、注释、提交信息）均使用中文
- **命名**: 遵循 PEP 8 规范，使用蛇形命名法（snake_case）

### 架构模式

项目采用**分层架构**，职责清晰分离：

```
src/
├── core/           # 核心业务逻辑
│   ├── config.py       # 配置管理（三级优先级）
│   ├── parser.py       # SVN 状态解析
│   ├── commit.py       # 提交执行
│   ├── svn_executor.py # SVN 命令封装
│   └── fs_helper.py    # 文件系统辅助
├── ai/             # AI 模块
│   ├── factory.py      # 消息生成工厂
│   ├── generator.py    # AI 生成器
│   ├── fallback.py     # 降级方案
│   └── diff.py         # diff 获取
├── utils/          # 工具模块
│   ├── filters.py      # 文件过滤
│   └── regex_cache.py  # 正则缓存
└── cli.py          # 命令行入口
```

**关键设计决策**:

1. **配置三级优先级**: 项目级 → 用户级 → 默认配置
2. **策略模式**: AI 生成优先，失败时自动降级到关键词匹配
3. **可选依赖**: PyQt5 通过 ImportError 处理，CLI 可独立运行
4. **平台兼容**: Windows 优先使用 TortoiseProc，回退到命令行 SVN

### 测试策略

- **单元测试**: 使用 pytest 覆盖核心业务逻辑
- **GUI 测试**: 使用 pytest-qt 测试 PyQt5 组件
- **测试覆盖**: 重点测试配置加载、状态解析、消息生成流程
- **运行方式**: `pytest` 命令执行所有测试

### Git工作流

- **分支策略**: 使用 main 作为主分支
- **提交格式**: 遵循 Conventional Commits 规范
  ```
  <type>(<scope>): <description>
  ```
- **提交类型**:
  - `feat` - 新功能
  - `fix` - 问题修复
  - `docs` - 文档变更
  - `style` - 代码格式
  - `refactor` - 重构
  - `perf` - 性能优化
  - `test` - 测试相关
  - `chore` - 构建/工具
  - `build` - 构建系统
- **提交范围**: guild, battle, chat, player, ui, network, config, art, audio

## 领域上下文

### SVN 状态码

解析器支持以下 SVN 状态码：

| 状态码 | 含义 | 处理方式 |
|--------|------|----------|
| M | Modified | 提交变更 |
| A | Added | 添加到版本控制 |
| D | Deleted | 从版本控制删除 |
| ? | Unversioned | 默认忽略，可通过配置包含 |
| ! | Missing | 需要恢复或删除 |
| C | Conflicted | 需要解决冲突 |
| R | Replaced | 替换 |
| ~ | Obstructed | 障碍 |
| S | Switched | 切换 |

### Conventional Commits 规范

项目严格遵循 Conventional Commits 格式，便于：

- 自动化变更日志生成
- 语义化版本控制
- 提交历史可读性
- CI/CD 流程集成

## 重要约束

### 技术约束

- **Python 版本**: 最低支持 Python 3.8
- **SVN 依赖**: 必须安装 SVN 命令行工具或 TortoiseSVN（Windows）
- **GUI 可选**: PyQt5 安装失败不应影响 CLI 功能

### 平台约束

- **Windows**:
  - PowerShell 使用 `;` 分隔命令（而非 `&&`）
  - 中文路径必须用引号包裹
  - 临时文件使用 `delete=False` 确保 SVN 可读取
- **Linux/Mac**: 用户配置目录为 `~/.config/smart-svn-commit/`

### 安全约束

- **禁止硬编码密钥**: API Key 通过配置文件管理，不提交到代码库
- **敏感文件保护**: `.env`、credentials 等文件不在版本控制中
- **输入验证**: 用户输入在系统边界必须验证

## 外部依赖

### 必需依赖

- **SVN 命令行工具** - 执行版本控制操作
- **TortoiseSVN**（Windows 推荐） - 提供更好的用户体验

### 可选依赖

- **OpenAI API** - AI 提交消息生成（需 API Key）
- **PyQt5** - GUI 界面支持

### 命令行入口

安装后注册两个命令：

- `smart-svn-commit` - 完整命令
- `ssc` - 短命令别名
