# 开发笔记

记录开发过程中的上下文和决策。

## 参考

以 [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) 作为开发蓝本。

## 传输层实现笔记

### Stdio 传输

- 客户端：`StdioClientTransport` 管理子进程
- 消息通过 stdin/stdout 传输
- 支持 `StdioStream::Inherit` 和 `StdioStream::Pipe`

### HTTP/SSE 传输

#### 设计决策

1. **框架无关的处理器** - `HttpServerHandler` 可以与任何 HTTP 框架集成
2. **axum 作为首选集成** - 提供 `create_router()` 快速创建完整路由
3. **双向通信** - 使用 tokio broadcast channel 实现服务端主动推送
4. **断线重连** - `EventBuffer` 缓存事件，支持 Last-Event-ID 回放

#### 技术选型

- **axum** - 现代异步 HTTP 框架，SSE 支持良好
- **tokio broadcast** - 多订阅者消息广播
- **async-stream** - 简化异步流创建

## 与 TypeScript SDK 的差异

### 已对齐

- Stdio 传输
- HTTP/SSE 传输（Streamable HTTP）
- Tools/Resources/Prompts 注册和调用
- Tasks API
- list_changed 通知

### 未实现

- OAuth 授权流程
- DNS 重绑定保护
- Sampling/Elicitation
- WebSocket 传输
- Completions

## 代码组织原则

参见 [AGENTS.md](../../AGENTS.md)：

- 代码尽可能按文件组织
- 一个类型一个文件
- 测试文件独立放置

## 测试策略

- 单元测试：与源码同文件或同目录
- 集成测试：`tests/` 目录
- 示例：`examples/` 目录
