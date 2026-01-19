# 变更日志

本文档记录 MCP Rust SDK 的主要变更。

## [Unreleased]

### 新增

- **HTTP/SSE 传输完整实现** (2026-01-19)
  - 真正的 SSE 长连接流（使用 axum）
  - 双向消息推送（`SseBroadcaster`）
  - Last-Event-ID 断线重连回放（`EventBuffer`）
  - CORS 支持
  - axum 框架集成（`create_router`、`AxumHandlerState`）

- **HTTP/SSE 集成测试** (2026-01-19)
  - POST 请求/响应测试
  - SSE 连接建立测试
  - 会话管理测试
  - 事件缓冲区和广播器测试
  - CORS 测试

### 变更

- **示例服务端升级** (2026-01-19)
  - `examples/http-server` 从 `tiny_http` 迁移到 `axum`
  - 支持真正的 SSE 流式响应

### 新增文件

- `server/src/http/axum_handler.rs` - axum 集成
- `server/src/http/broadcast.rs` - SSE 广播和事件缓冲
- `server/tests/http_sse.rs` - HTTP/SSE 集成测试

---

## 之前的变更

### 基础功能

- **Stdio 传输** - 客户端和服务端的 stdio 传输实现
- **MCP 核心协议** - JSON-RPC 消息处理
- **Tools/Resources/Prompts** - 注册和调用
- **Tasks API** - `tasks/get/list/result/cancel`
- **list_changed 通知** - 工具/资源/提示变更通知
- **Logging** - `logging/setLevel` 支持

### HTTP/SSE 基础

- **HTTP 客户端传输** - `HttpClientTransport`
- **HTTP 服务端处理器** - `HttpServerHandler`（框架无关）
- **会话管理** - `SessionManager`
- **SSE 解析** - `SseParser`、`SseReader`
- **重连策略** - `ReconnectOptions`

---

## 版本说明

本项目目前处于开发阶段，尚未发布正式版本。以上变更记录按时间顺序记录主要功能的实现。

### 与 TypeScript SDK 的差异

详见 [状态总览](./status.md) 了解与 TypeScript SDK 的功能对比。

主要未实现的功能：
- OAuth 授权
- DNS 重绑定保护
- Sampling/Elicitation
- WebSocket 传输
