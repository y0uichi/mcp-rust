# 旧版 HTTP+SSE 传输

本文档说明旧版 HTTP+SSE 传输（协议版本 2024-11-05）的实现和使用方式。

> **注意**: 此传输已被废弃，仅用于向后兼容旧版 MCP 客户端。新实现应使用 Streamable HTTP。

## 与 Streamable HTTP 的区别

| 特性 | 旧版 SSE (2024-11-05) | Streamable HTTP (2025-03-26) |
|------|----------------------|------------------------------|
| 会话 ID | URL 查询参数 `?sessionId=xxx` | `Mcp-Session-Id` 头部 |
| 端点事件 | 发送 `endpoint` 事件告知客户端 POST 地址 | 不需要 endpoint 事件 |
| POST 响应 | 返回 202 Accepted (无内容) | 返回 JSON 响应或 SSE 流 |
| 重连支持 | 无 Last-Event-ID 支持 | 支持 Last-Event-ID 回放 |

## 协议流程

```
Client                              Server
  │                                   │
  │  GET /sse                         │
  │  Accept: text/event-stream        │
  │──────────────────────────────────▶│
  │                                   │
  │  event: endpoint                  │
  │  data: /message?sessionId=xxx     │
  │◀──────────────────────────────────│
  │                                   │
  │  POST /message?sessionId=xxx      │
  │  (JSON-RPC Request)               │
  │──────────────────────────────────▶│
  │                                   │
  │  202 Accepted                     │
  │◀──────────────────────────────────│
  │                                   │
  │  event: message                   │
  │  data: (JSON-RPC Response)        │
  │◀──────────────────────────────────│
```

## 服务端使用

### 依赖配置

```toml
[dependencies]
mcp_server = { path = "server", features = ["axum"] }
tokio = { version = "1.0", features = ["full"] }
axum = "0.7"
```

### 仅旧版 SSE

```rust
use std::sync::Arc;
use mcp_server::{
    McpServer, ServerOptions, LegacySseConfig, LegacySseState, create_legacy_sse_router,
};

let mcp_server = Arc::new(McpServer::new(server_info, server_options));

// 配置旧版 SSE
let config = LegacySseConfig {
    endpoint_path: "/sse".to_string(),
    message_path: "/message".to_string(),
};

let state = Arc::new(LegacySseState::new(mcp_server, config));
let app = create_legacy_sse_router(state);

// 启动服务器
let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await?;
axum::serve(listener, app).await?;
```

### 同时支持新旧协议（推荐）

```rust
use std::sync::Arc;
use mcp_server::{
    McpServer, ServerOptions,
    AxumHandlerConfig, AxumHandlerState, create_router,
    LegacySseConfig, LegacySseState, create_legacy_sse_router,
};

let mcp_server = Arc::new(McpServer::new(server_info, server_options));

// 创建 Streamable HTTP 路由
let streamable_config = AxumHandlerConfig {
    endpoint_path: "/mcp".to_string(),
    ..Default::default()
};
let streamable_state = Arc::new(AxumHandlerState::new(Arc::clone(&mcp_server), streamable_config));
let streamable_router = create_router(streamable_state);

// 创建旧版 SSE 路由
let legacy_config = LegacySseConfig {
    endpoint_path: "/sse".to_string(),
    message_path: "/message".to_string(),
};
let legacy_state = Arc::new(LegacySseState::new(Arc::clone(&mcp_server), legacy_config));
let legacy_router = create_legacy_sse_router(legacy_state);

// 合并路由
let app = streamable_router.merge(legacy_router);

// 启动服务器
let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await?;
axum::serve(listener, app).await?;
```

## 客户端使用

### 依赖配置

```toml
[dependencies]
mcp_client = { path = "client" }
```

### 基础示例

```rust
use mcp_client::http::{LegacySseClientConfig, LegacySseClientTransport};

// 创建配置
let config = LegacySseClientConfig::new("http://localhost:8080")
    .sse_path("/sse");

// 创建传输层
let mut transport = LegacySseClientTransport::new(config);

// 注册事件处理器
transport
    .on_message(|msg| {
        println!("Received: {:?}", msg);
    })
    .on_error(|err| {
        eprintln!("Error: {:?}", err);
    })
    .on_close(|| {
        println!("Connection closed");
    });

// 启动连接
transport.start()?;

// 发送消息
transport.send(&JsonRpcMessage::Request(/* ... */))?;

// 关闭连接
transport.close()?;
```

## 端点

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | /sse | 建立 SSE 连接，接收 `endpoint` 事件 |
| POST | /message?sessionId=xxx | 发送 JSON-RPC 消息 |

## 测试

```bash
# 运行兼容服务器示例
cargo run -p mcp-sse-compat-server

# 测试旧版 SSE 连接
curl -N http://localhost:8080/sse -H "Accept: text/event-stream"

# 将看到类似输出:
# event: endpoint
# data: /message?sessionId=abc123
```

## 示例

### 兼容服务器

同时支持 Streamable HTTP 和旧版 SSE：

```bash
cargo run -p mcp-sse-compat-server
```

端点：
- `POST/GET/DELETE /mcp` - Streamable HTTP
- `GET /sse` + `POST /message` - 旧版 SSE
