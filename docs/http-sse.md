# HTTP/SSE 传输

本文档详细说明 HTTP/SSE 传输层的实现和使用方式。

## 概述

HTTP/SSE 传输已完整实现，包括：

- 真正的 SSE 长连接流
- 双向消息推送（服务端主动推送）
- Last-Event-ID 断线重连回放
- CORS 支持
- axum 框架集成

## 架构

```
┌─────────────────┐                    ┌─────────────────┐
│   HTTP Client   │                    │   HTTP Server   │
│                 │                    │                 │
│ ┌─────────────┐ │   POST /mcp        │ ┌─────────────┐ │
│ │  Transport  │─┼───────────────────▶│ │   Handler   │ │
│ └─────────────┘ │                    │ └─────────────┘ │
│                 │   GET /mcp (SSE)   │        │        │
│ ┌─────────────┐ │◀──────────────────┼│ ┌─────────────┐ │
│ │  SseReader  │ │                    │ │ Broadcaster │ │
│ └─────────────┘ │                    │ └─────────────┘ │
│                 │                    │        │        │
│ ┌─────────────┐ │                    │ ┌─────────────┐ │
│ │  Reconnect  │ │   Last-Event-ID    │ │EventBuffer  │ │
│ └─────────────┘ │───────────────────▶│ └─────────────┘ │
└─────────────────┘                    └─────────────────┘
```

## 服务端使用

### 依赖配置

```toml
[dependencies]
mcp_server = { path = "server", features = ["axum"] }
tokio = { version = "1.0", features = ["full"] }
axum = "0.7"
```

### 基础示例

```rust
use std::sync::Arc;
use mcp_core::types::{BaseMetadata, Icons, Implementation, ServerCapabilities};
use mcp_server::{
    AxumHandlerConfig, AxumHandlerState, McpServer, ServerOptions, create_router,
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 创建服务器信息
    let server_info = Implementation {
        base: BaseMetadata {
            name: "my-mcp-server".to_string(),
            title: Some("My MCP Server".to_string()),
        },
        icons: Icons::default(),
        version: "0.1.0".to_string(),
        website_url: None,
        description: Some("My MCP server description".to_string()),
    };

    // 配置服务器能力
    let mut server_options = ServerOptions::default();
    server_options.capabilities = Some(ServerCapabilities {
        tools: Some(mcp_core::types::ToolCapabilities {
            list_changed: Some(true),
        }),
        ..Default::default()
    });

    // 创建 MCP 服务器
    let mcp_server = Arc::new(McpServer::new(server_info, server_options));

    // 配置 HTTP 处理器
    let config = AxumHandlerConfig {
        base_url: Some("http://localhost:8080".to_string()),
        endpoint_path: "/mcp".to_string(),
        keep_alive_interval: std::time::Duration::from_secs(30),
        broadcast_capacity: 100,
        enable_cors: true,
        ..Default::default()
    };

    // 创建路由
    let state = Arc::new(AxumHandlerState::new(mcp_server, config));
    let app = create_router(state);

    // 启动服务器
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await?;
    println!("Server listening on http://0.0.0.0:8080");
    axum::serve(listener, app).await?;

    Ok(())
}
```

### 配置选项

```rust
pub struct AxumHandlerConfig {
    /// 会话配置
    pub session_config: SessionConfig,
    /// 事件缓冲区配置（用于 Last-Event-ID 回放）
    pub event_buffer_config: EventBufferConfig,
    /// 服务器基础 URL
    pub base_url: Option<String>,
    /// 端点路径（默认: "/mcp"）
    pub endpoint_path: String,
    /// SSE 保活间隔
    pub keep_alive_interval: Duration,
    /// 每个会话的广播通道容量
    pub broadcast_capacity: usize,
    /// 是否启用 CORS
    pub enable_cors: bool,
}
```

### 服务端主动推送

```rust
// 获取 handler state
let state: Arc<AxumHandlerState> = /* ... */;

// 向特定会话推送消息
let message = JsonRpcMessage::Notification(/* ... */);
state.broadcast_to_session("session-id", message).await?;
```

## 客户端使用

### 依赖配置

```toml
[dependencies]
mcp_client = { path = "client" }
```

### 基础示例

```rust
use mcp_client::http::{HttpClientConfig, HttpClientTransport};

// 创建配置
let config = HttpClientConfig::new("http://localhost:8080/mcp")
    .auto_reconnect(true)
    .custom_header("Authorization", "Bearer token");

// 创建传输层
let mut transport = HttpClientTransport::new(config);

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

## API 端点

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | /mcp | 发送 JSON-RPC 消息 |
| GET | /mcp | 建立 SSE 连接 |
| DELETE | /mcp | 关闭会话 |

### 请求头

| 头部 | 说明 |
| --- | --- |
| `Content-Type` | POST 请求必须为 `application/json` |
| `Accept` | GET 请求必须包含 `text/event-stream` |
| `Mcp-Session-Id` | 会话 ID（可选，服务器会在响应中返回） |
| `Last-Event-ID` | 用于断线重连回放（可选） |

## 断线重连

客户端支持自动重连，配置选项：

```rust
pub struct ReconnectOptions {
    /// 初始重连延迟
    pub initial_delay: Duration,
    /// 最大重连延迟
    pub max_delay: Duration,
    /// 延迟倍增因子
    pub backoff_factor: f64,
    /// 最大重试次数（None 表示无限）
    pub max_attempts: Option<u32>,
}
```

当重连时，客户端会：
1. 发送 `Last-Event-ID` 头部
2. 服务端从 `EventBuffer` 中回放错过的事件
3. 继续接收新事件

## 测试

```bash
# 运行集成测试
cargo test -p mcp_server --features axum --test http_sse

# 启动示例服务器
cargo run -p mcp-http-server

# 测试 POST 请求
curl -X POST http://localhost:8080/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"0.1.0"}}}'

# 测试 SSE 连接
curl -N http://localhost:8080/mcp -H "Accept: text/event-stream"
```
