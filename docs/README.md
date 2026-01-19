# MCP Rust 文档

本目录包含 MCP Rust SDK 的开发文档。

## 文档结构

| 文档 | 说明 |
| --- | --- |
| [状态总览](./status.md) | 功能完成状态和与 TypeScript SDK 的对比 |
| [HTTP/SSE 传输](./http-sse.md) | HTTP/SSE 传输层详细文档和使用指南 |
| [WebSocket 传输](./websocket.md) | WebSocket 传输层详细文档和使用指南 |
| [旧版 SSE 传输](./legacy-sse.md) | 旧版 HTTP+SSE 兼容传输（2024-11-05） |
| [架构概览](./architecture.md) | 模块结构和文件清单 |
| [开发指南](./dev/dev.md) | 开发进展和上下文记录 |
| [变更日志](./CHANGELOG.md) | 版本变更记录 |

## 快速状态（2026-01-19）

| 模块 | 状态 |
| --- | --- |
| Stdio 传输 | ✅ 完成 |
| HTTP/SSE 传输 | ✅ 完成 |
| WebSocket 传输 | ✅ 完成 |
| 旧版 SSE 兼容传输 | ✅ 完成 |
| Tools/Resources/Prompts | ✅ 完成 |
| Tasks API | ✅ 完成 |
| OAuth/DNS 保护 | ❌ 未开始 |
| Sampling/Elicitation | ❌ 未开始 |

## 快速开始

### 安装依赖

```toml
# 基础功能
[dependencies]
mcp_core = { path = "core" }
mcp_server = { path = "server" }
mcp_client = { path = "client" }

# 启用 HTTP/SSE（axum）
mcp_server = { path = "server", features = ["axum"] }
```

### 运行示例

```bash
# 构建所有包
cargo build

# 运行 stdio 文件系统示例
cargo run -p mcp_examples --bin filesystem

# 运行 HTTP 服务器
cargo run -p mcp-http-server

# 运行 HTTP 客户端
cargo run -p mcp-http-client
```

### 运行测试

```bash
# 运行所有测试
cargo test --workspace

# 运行 HTTP/SSE 集成测试
cargo test -p mcp_server --features axum --test http_sse
```

## 参考

- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) - 本项目的参考实现
- [MCP 规范](https://spec.modelcontextprotocol.io/) - Model Context Protocol 规范
