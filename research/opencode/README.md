# OpenCode 研究报告

## 概述

OpenCode 是一个开源的 AI 编程代理工具，主要运行在终端环境中。它可以作为 Claude Code、Cursor、Codex 等工具的替代品。

**官网**: https://opencode.ai/

**GitHub**: https://github.com/opencode-ai/opencode (SST 版本)

## 重要背景：OpenCode 与 Crush 的分裂

2025年发生了一次重要的项目分裂：

1. **原始创建者** Kujtim Hoxha 加入了 Charm 团队
2. **Charm** 收购了原始项目并将其重命名为 **Crush** (https://github.com/charmbracelet/crush)
3. **SST 团队**（Dax 和 Adam）fork 了项目，继续以 **OpenCode** 名义维护

**当前状态（2026年）**:
- **OpenCode** (SST): 继续作为独立开源项目，48,000+ GitHub stars
- **Crush** (Charm): 原作者继续开发的版本

## 核心特性

### 1. 多平台支持
- 终端界面（主要）
- 桌面应用（macOS、Windows、Linux - Beta）
- IDE 扩展
- LSP（语言服务协议）集成

### 2. AI 模型支持
支持 75+ LLM 提供商，包括：

| 提供商 | 支持的模型 |
|--------|-----------|
| **OpenAI** | GPT-4.1, GPT-4.5 Preview, GPT-4o, O1/O3 系列 |
| **Anthropic** | Claude 4 Sonnet/Opus, Claude 3.5/3.7 Sonnet, Claude 3 Haiku/Opus |
| **Google** | Gemini 2.5, 2.5 Flash, 2.0 Flash |
| **GitHub Copilot** | GPT-4/4o, Claude 3.5/3.7, O1/O3, Gemini 2.0/2.5 |
| **AWS Bedrock** | Claude 3.7 Sonnet |
| **Groq** | Llama 4, QWEN QWQ-32b, Deepseek R1 |
| **Azure OpenAI** | GPT-4.1, GPT-4.5 Preview, O1/O3 |
| **Google VertexAI** | Gemini 2.5 系列 |

还支持本地模型。

### 3. 核心功能
- **多会话支持**: 可在同一项目上运行多个并行代理
- **会话共享**: 通过链接分享会话
- **会话持久化**: SQLite 存储
- **工具集成**: AI 可执行命令、搜索文件、修改代码
- **Vim 风格编辑器**: 内置文本编辑功能
- **文件追踪**: 监控和可视化会话期间的更改
- **外部编辑器支持**: 可使用首选编辑器编写消息
- **自动压缩**: 当接近上下文窗口限制时自动总结对话

### 4. 工作模式
- **Plan 模式**: 策略规划（按 Tab 切换）
- **Build 模式**: 实际实现

## 安装方式

```bash
# 快速安装脚本
curl -fsSL https://opencode.ai/install | bash

# Homebrew (macOS)
brew install opencode-ai/tap/opencode

# npm
npm install -g opencode

# Go
go install github.com/opencode-ai/opencode@latest

# AUR (Arch Linux)
yay -S opencode-ai-bin
```

## 配置

配置文件搜索顺序：
1. `$HOME/.opencode.json`
2. `$XDG_CONFIG_HOME/opencode/.opencode.json`
3. `./.opencode.json`（当前目录）

支持通过环境变量或 JSON 配置文件设置 API 密钥。

## 使用方式

### 交互模式
```bash
opencode
```

### 非交互模式
```bash
opencode -p "your prompt"
opencode -p "your prompt" -f json  # JSON 输出
opencode -p "your prompt" -q       # 静默模式
```

### 常用命令
- `/connect` - 连接 LLM 提供商
- `/init` - 分析项目并生成 AGENTS.md
- `/undo` - 撤销更改
- `/redo` - 重做更改
- `/share` - 分享对话
- `@文件名` - 引用文件

## 与竞品对比

### OpenCode vs Claude Code vs Cursor

| 特性 | OpenCode | Claude Code | Cursor |
|------|----------|-------------|--------|
| **价格** | 免费（需自付 API 费用） | $17-100/月 + API | $20/月 Pro |
| **开源** | ✅ 完全开源 | ❌ | ❌ |
| **模型灵活性** | 75+ 提供商 | 仅 Claude | 多模型 |
| **界面** | 终端/桌面/IDE | 终端 | 完整 IDE |
| **自主性** | 高 | 非常高 | 中等（交互式） |
| **设置难度** | 中等 | 中等 | 简单 |

### 各工具优势

**OpenCode 优势**:
- 完全开源，可自托管
- 模型灵活性最高，不被锁定
- 免费（仅需 API 费用）
- 支持本地模型

**Claude Code 优势**:
- 深度推理能力最强
- 大规模重构和复杂项目设置最佳
- 端到端优化（模型与工具同一公司）
- 自主多文件操作能力强

**Cursor 优势**:
- 开箱即用，设置最简单
- 实时交互式编码最佳
- 完整 IDE 体验
- 对新手最友好

### 开发者观点

> "OpenCode 的开发者自己说：'我们逆向工程了 Claude Code，并重新实现了几乎完全相同的逻辑。'"

> "OpenCode 是开源且模型无关的...今天最好的代理编码模型是 Anthropic，但明天可能会改变。如果改变了，我不想被锁定在 Claude Code 中。"

## 技术栈

- **语言**: Go
- **TUI 框架**: Bubble Tea (Charm)
- **存储**: SQLite
- **协议**: LSP (Language Server Protocol)

## 隐私

- 隐私优先设计
- 不存储代码或上下文数据
- 可完全自托管

## 推荐使用场景

1. **优先选择 OpenCode 当**:
   - 需要模型灵活性和未来可切换性
   - 预算有限但愿意配置
   - 需要自托管或企业私有部署
   - 偏好终端工作流

2. **优先选择 Claude Code 当**:
   - 需要最强的推理和自主能力
   - 进行大规模重构或复杂项目
   - 愿意支付更高费用获得最佳体验

3. **优先选择 Cursor 当**:
   - 需要完整 IDE 体验
   - 偏好实时交互式协助
   - 是 AI 编码工具新手

## 相关资源

- [OpenCode 官网](https://opencode.ai/)
- [OpenCode GitHub (SST)](https://github.com/opencode-ai/opencode)
- [Crush GitHub (Charm)](https://github.com/charmbracelet/crush)
- [OpenCode 文档](https://opencode.ai/docs)

## 参考来源

- [OpenCode vs Claude Code vs Cursor: 2026 对比](https://www.nxcode.io/resources/news/opencode-vs-claude-code-vs-cursor-2026)
- [OpenCode vs Claude Code: 2026 Battle Guide](https://byteiota.com/opencode-vs-claude-code-2026-battle-guide-48k-vs-47k/)
- [From Cursor to Claude Code & OpenCode](https://www.groff.dev/blog/claude-code-opencode-productivity-boost)
- [Terminal Agents: Codex vs. Crush vs. OpenCode vs. Cursor CLI vs. Claude Code](https://app.daily.dev/posts/terminal-agents-codex-vs-crush-vs-opencode-vs-cursor-cli-vs-claude-code-geyyw8ohw)
- [Charm's New AI Coding Agent "Crush" Emerges from OpenCode Controversy](https://biggo.com/news/202507310715_Charm_Crush_AI_Coding_Agent)
