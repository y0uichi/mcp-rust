# Rust MCP 客户端指南

这个文档聚焦于如何在 Rust 中实现一个基于 MCP 核心库的客户端。重点介绍客户端的核心设计要素，如何借助 `mcp_core` 提供的协议类型，以及利用标准输入/输出（stdio）快速验证的演示代码。

## 1. 客户端架构概览

### 配置与角色
- 启动时复用 `mcp_core::CoreConfig`（或 `mcp_core::prelude::Config`）来统一服务名称、监听端口和环境信息。客户端通常通过 `CoreConfig::dev("mcp-client")` 取得默认设置，再调用 `Role::Client` 记录自己的角色。
- `CoreConfig` 也能注入部署特定的端口与环境，使得日志/调试信息与部署工具保持一致。

### 消息构建
- 所有 MCP 消息结构（`Message`, `RequestMessage`, `NotificationMessage` 等）都定义在 `mcp_core::types` 中。客户端以 `Message::new(sender, recipient, body)` 创建通用消息，并可调用 `summary` 生成 CLI 日志。
- `RequestMessage::new(id, method, params)` 与 `ResultMessage::success(...)` 在客户端与服务器之间建立 JSON-RPC 风格的请求/响应链路，而 `SchemaValidator` 确保参数格式满足预期。

### 协议与处理
- 如果客户端需要伪装为服务端（例如在测试里模拟回应），可复用 `mcp_core::Protocol` 和 `RequestHandler`。客户端注册处理器并为每个方法提供对应的 schema，Protocol 会自动校验并执行。
- 多数场景下，客户端只需要构建请求并通过 `stdin`/网络写入，而无需驻留在 handler 内，因此可以把 `Protocol` 当做一个可复用的工具箱，用于在未来上线时加入 schema 级别的参数校验。

### 通信层设计建议
- 把与终端或传输层的交互封装在 `ClientRuntime<R: BufRead, W: Write>` 结构体，携带 `config`, `role`, 以及事件循环所需的输入输出。
- `ClientRuntime` 负责从 `BufRead` 读取外部事件（例如来自 `stdin` 或管道的数据），根据内容构造 `Message`/`RequestMessage`，再写入 `Write`（`stdout` 或套接字）。
- 将 `serde_json` 用于在文本流与结构体之间做序列化/反序列化，方便与 MCP 的 JSON-RPC 兼容。

## 2. 标准输入/输出（stdio）演示

下面的示例代码演示如何使用 stdio 构建简单的 MCP 客户端：它从 `stdin` 读取一行用户输入，打包成结构化的 `Message`，并把序列化后的 JSON 回写到 `stdout`，模拟与服务端的交换。

```rust
use mcp_core::{CoreConfig, Message, Role};
use serde_json::json;
use std::io::{self, BufRead, Write};

fn main() -> io::Result<()> {
    let config = CoreConfig::dev("mcp-cli-stdio");
    announce_role(Role::Client, &config);

    let stdin = io::stdin();
    let mut stdout = io::stdout();

    writeln!(stdout, "请输入要发送的消息：")?;
    stdout.flush()?;

    for line in stdin.lock().lines().flatten() {
        if line.trim().is_empty() {
            writeln!(stdout, "收到空行，退出。")?;
            break;
        }

        let message = Message::new(&config.service_name, "mcp-server", &line);
        let request = json!({
            "jsonrpc": "2.0",
            "id": "stdin-1",
            "method": "chat_message",
            "params": { "body": message.body, "recipient": message.recipient }
        });

        writeln!(stdout, "发送：{}", message.summary())?;
        writeln!(stdout, "JSON-RPC payload: {}", request)?;
        stdout.flush()?;
    }

    Ok(())
}
```

此演示强调：

- 通过 `stdin.lock().lines()` 遍历用户输入，方便在非 GUI 环境下驱动 MCP 客户端。
- 利用 `Message` 统一日志输出，与 `serde_json::json!` 构造请求，保持 JSON-RPC 2.0 兼容性。
- 在真实部署中，`stdout` 可对接跨进程管道或 WebSocket，替代简单的终端输出。

## 3. 客户端必要组件与下一步

### 必备组件
- `CoreConfig`：定义服务名称、端口、环境选择，供日志与网络共识使用。
- `Role::Client` 与 `announce_role`：明确身份并记录运行模式，便于运维排障。
- `Message` 以及 JSON-RPC 类型：维持与服务器的通信格式，必要时引入 `Protocol` 校验参数。
- `serde_json` + `std::io`：桥接文本流与结构化消息，特别是在 stdio 或管道场景。

### 后续扩展建议
1. 引入 `mcp_core::schema::JsonSchemaValidator` 为客户端的出站请求参数做结构校验。
2. 封装一个可配置的 `ClientRuntime`，支持不同的传输（stdio、TCP、WebSocket）。
3. 为每条 `RequestMessage` 生成唯一 `MessageId`，并在收到 `ResultMessage` 时通过 `serde_json` 解析并显示结果。

通过以上结构，你可以在当前 workspace 的 `client` crate 中逐步扩展功能，从 stdio 验证版过渡到网络级的 MCP 客户端。 阅读核心模块（`core/src/types.rs`, `core/src/protocol.rs`）可以帮助你在实现时复用已有工具。
