# 架构概览

本文档描述 MCP Rust SDK 的模块结构和文件组织。

## 工作区结构

```
mcp-rust/
├── core/                 # 核心库 (mcp_core)
├── server/               # 服务端库 (mcp_server)
├── client/               # 客户端库 (mcp_client)
├── examples/             # 示例代码
│   ├── http-server/      # HTTP 服务端示例
│   ├── http-client/      # HTTP 客户端示例
│   ├── websocket-server/ # WebSocket 服务端示例
│   ├── sse-compat-server/# 兼容服务器（支持新旧协议）
│   ├── mcp-filesystem-server/
│   └── mcp-filesystem-client/
└── docs/                 # 文档
```

## 核心库 (mcp_core)

共享的类型定义、协议和工具。

```
core/src/
├── http/                 # HTTP 传输相关
│   ├── mod.rs           # 模块入口
│   ├── session.rs       # SessionId、ResumptionToken
│   ├── sse.rs           # SseEvent、SseParser、头部常量
│   ├── transport.rs     # ConnectionState、AsyncTransport trait
│   └── error.rs         # HTTP 传输错误类型
├── protocol/            # MCP 协议
├── stdio/               # Stdio 传输
├── types/               # 类型定义
└── lib.rs
```

### 关键类型

| 类型 | 说明 |
| --- | --- |
| `SessionId` | 会话标识符 |
| `ResumptionToken` | 断线重连令牌 |
| `SseEvent` | SSE 事件（Message, Ping, SessionReady, Endpoint） |
| `SseParser` | SSE 流增量解析器 |
| `ConnectionState` | 连接状态机 |
| `JsonRpcMessage` | JSON-RPC 消息 |

## 服务端库 (mcp_server)

MCP 服务端实现。

```
server/src/
├── http/                 # HTTP 传输
│   ├── mod.rs           # 模块入口
│   ├── handler.rs       # HttpServerHandler（框架无关）
│   ├── axum_handler.rs  # axum 集成（feature = "axum"）
│   ├── legacy_sse.rs    # 旧版 SSE 兼容传输
│   ├── broadcast.rs     # SseBroadcaster、EventBuffer
│   ├── session_manager.rs  # SessionManager
│   ├── sse_writer.rs    # SseWriter、SseResponseBuilder
│   └── error.rs         # HTTP 服务端错误
├── websocket/           # WebSocket 传输
│   ├── mod.rs           # 模块入口
│   └── axum_handler.rs  # axum WebSocket 集成（feature = "websocket"）
├── server/              # MCP 服务器核心
│   ├── mod.rs
│   ├── mcp_server.rs    # McpServer 主结构
│   ├── server.rs        # Server trait
│   ├── handlers/        # 请求处理器
│   └── registries/      # 工具/资源/提示注册表
├── tests/               # 集成测试
│   └── http_sse.rs      # HTTP/SSE 测试
└── lib.rs
```

### 关键类型

| 类型 | 说明 |
| --- | --- |
| `McpServer` | MCP 服务器主结构 |
| `HttpServerHandler` | 框架无关的 HTTP 处理器 |
| `AxumHandlerState` | axum 集成状态 |
| `SessionManager` | 会话管理器 |
| `SseBroadcaster` | SSE 消息广播器 |
| `EventBuffer` | 事件缓冲区（Last-Event-ID 回放） |
| `WebSocketState` | WebSocket 连接管理 |
| `LegacySseState` | 旧版 SSE 状态管理 |

### Feature Flags

| Feature | 说明 |
| --- | --- |
| `axum` | 启用 axum 框架集成（HTTP/SSE） |
| `websocket` | 启用 WebSocket 支持（包含 axum） |
| `tokio` | 启用 tokio 运行时支持 |

## 客户端库 (mcp_client)

MCP 客户端实现。

```
client/src/
├── http/                 # HTTP 传输
│   ├── mod.rs           # 模块入口
│   ├── transport.rs     # HttpClientTransport
│   ├── config.rs        # HttpClientConfig
│   ├── legacy_sse.rs    # 旧版 SSE 客户端传输
│   ├── reconnect.rs     # ReconnectOptions、ReconnectState
│   ├── sse_reader.rs    # SseReader
│   └── error.rs         # HTTP 客户端错误
├── websocket/           # WebSocket 传输
│   ├── mod.rs           # 模块入口
│   ├── transport.rs     # WebSocketClientTransport
│   └── error.rs         # WebSocket 客户端错误
├── stdio/               # Stdio 传输
│   ├── mod.rs
│   ├── transport.rs     # StdioClientTransport
│   └── params.rs        # StdioServerParameters
├── client/              # MCP 客户端核心
│   ├── mod.rs
│   ├── client.rs        # Client 主结构
│   └── ...
└── lib.rs
```

### 关键类型

| 类型 | 说明 |
| --- | --- |
| `Client` | MCP 客户端主结构 |
| `HttpClientTransport` | HTTP 传输层 |
| `HttpClientConfig` | HTTP 配置 |
| `ReconnectOptions` | 重连策略配置 |
| `SseReader` | SSE 流读取器 |
| `WebSocketClientTransport` | WebSocket 传输层 |
| `LegacySseClientTransport` | 旧版 SSE 传输层 |
| `StdioClientTransport` | Stdio 传输层 |

## 示例代码

### HTTP 服务端 (examples/http-server)

使用 axum 的完整 HTTP 服务端示例。

```bash
cargo run -p mcp-http-server
```

### HTTP 客户端 (examples/http-client)

HTTP 客户端示例。

```bash
cargo run -p mcp-http-client
```

### WebSocket 服务端 (examples/websocket-server)

使用 axum 的 WebSocket 服务端示例。

```bash
cargo run -p mcp-websocket-server
```

### 兼容服务器 (examples/sse-compat-server)

同时支持 Streamable HTTP 和旧版 SSE 的服务端示例。

```bash
cargo run -p mcp-sse-compat-server
```

### 文件系统示例 (examples/mcp-filesystem-*)

与 `@modelcontextprotocol/server-filesystem` 交互的示例。

```bash
cargo run -p mcp_examples --bin filesystem
```

## 数据流

### 请求/响应流程

```
Client                          Server
  │                               │
  │  POST /mcp (JSON-RPC Request) │
  │──────────────────────────────▶│
  │                               │
  │                               ├──▶ handle_request()
  │                               │
  │  JSON-RPC Response            │
  │◀──────────────────────────────│
```

### SSE 流程

```
Client                          Server
  │                               │
  │  GET /mcp (Accept: SSE)       │
  │──────────────────────────────▶│
  │                               │
  │  event: session               │
  │◀──────────────────────────────│
  │                               │
  │  event: message (push)        │
  │◀──────────────────────────────│
  │                               │
  │  :ping                        │
  │◀──────────────────────────────│
  │                               │
```

### 断线重连

```
Client                          Server
  │                               │
  │  Connection lost              │
  │  ✕ ✕ ✕ ✕ ✕ ✕ ✕ ✕ ✕ ✕ ✕ ✕ ✕  │
  │                               │
  │  GET /mcp                     │
  │  Last-Event-ID: xxx-42        │
  │──────────────────────────────▶│
  │                               │
  │                               ├──▶ EventBuffer.events_after("xxx-42")
  │                               │
  │  Replay missed events         │
  │◀──────────────────────────────│
  │                               │
  │  Continue streaming           │
  │◀──────────────────────────────│
```
