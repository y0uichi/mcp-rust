# WebSocket 传输

本文档详细说明 WebSocket 传输层的实现和使用方式。

## 概述

WebSocket 传输提供全双工双向通信，适用于：

- 浏览器客户端
- 需要实时双向通信的场景
- 简化的连接管理（单一连接）

## 特性

- 全双工 WebSocket 通信
- MCP 子协议协商（`Sec-WebSocket-Protocol: mcp`）
- 自动 ping/pong 处理
- CORS 支持
- axum 框架集成

## 与 HTTP/SSE 对比

| 特性 | WebSocket | HTTP/SSE |
| --- | --- | --- |
| 通信方向 | 全双工 | 半双工（POST + SSE） |
| 连接数 | 1 | 2（POST + SSE） |
| 会话管理 | 连接即会话 | 需要 Session ID |
| 断线重连 | 需自行实现 | Last-Event-ID 回放 |
| 浏览器支持 | 原生支持 | SSE 有限制 |

## 服务端使用

### 依赖配置

```toml
[dependencies]
mcp_server = { path = "server", features = ["websocket"] }
tokio = { version = "1.0", features = ["full"] }
axum = "0.7"
```

### 基础示例

```rust
use std::sync::Arc;
use mcp_core::types::{BaseMetadata, Icons, Implementation, ServerCapabilities};
use mcp_server::{
    McpServer, ServerOptions, WebSocketConfig, WebSocketState, create_websocket_router,
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

    // 配置 WebSocket 处理器
    let config = WebSocketConfig {
        endpoint_path: "/ws".to_string(),
        enable_cors: true,
        channel_buffer_size: 100,
    };

    // 创建路由
    let state = Arc::new(WebSocketState::new(mcp_server, config));
    let app = create_websocket_router(state);

    // 启动服务器
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await?;
    println!("Server listening on ws://0.0.0.0:8080/ws");
    axum::serve(listener, app).await?;

    Ok(())
}
```

### 配置选项

```rust
pub struct WebSocketConfig {
    /// 端点路径（默认: "/ws"）
    pub endpoint_path: String,
    /// 是否启用 CORS
    pub enable_cors: bool,
    /// 每个连接的消息通道缓冲区大小
    pub channel_buffer_size: usize,
}
```

### 服务端主动推送

```rust
// 获取 handler state
let state: Arc<WebSocketState> = /* ... */;

// 向特定连接推送消息
let message = JsonRpcMessage::Notification(/* ... */);
state.send_to_connection("connection-id", message).await?;

// 广播给所有连接
state.broadcast(message).await;
```

## 客户端使用

### 依赖配置

```toml
[dependencies]
mcp_client = { path = "client", features = ["websocket"] }
tokio = { version = "1.0", features = ["full"] }
```

### 基础示例

```rust
use mcp_client::websocket::WebSocketClientTransport;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 创建传输层
    let mut transport = WebSocketClientTransport::new("ws://localhost:8080/ws");

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
    transport.start().await?;

    // 发送消息
    let request = /* 构建 JSON-RPC 请求 */;
    transport.send(&request).await?;

    // 关闭连接
    transport.close().await?;

    Ok(())
}
```

## 协议详情

### 子协议

WebSocket 连接使用 MCP 子协议：

```
Sec-WebSocket-Protocol: mcp
```

### 消息格式

所有消息都是 JSON-RPC 2.0 格式的文本消息：

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}
```

## 测试

```bash
# 运行单元测试
cargo test -p mcp_server --features websocket
cargo test -p mcp_client --features websocket

# 启动示例服务器
cargo run -p mcp-websocket-server

# 使用 websocat 测试
websocat ws://localhost:8080/ws -H "Sec-WebSocket-Protocol: mcp"
```

## 示例请求

连接后发送：

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"0.1.0"}}}
```

列出工具：

```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

调用工具：

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"echo","arguments":{"message":"Hello!"}}}
```
