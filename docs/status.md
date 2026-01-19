# 功能状态总览

本文档记录 MCP Rust SDK 与 TypeScript SDK 的功能对比和完成状态。

## 状态总结

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| Stdio 传输 | ✅ 完成 | 客户端/服务端可用 |
| HTTP/SSE 传输 | ✅ 完成 | 使用 axum 实现真正的 SSE 流、双向推送、Last-Event-ID 回放 |
| WebSocket 传输 | ✅ 完成 | 使用 axum 实现全双工通信 |
| Tools/Resources/Prompts | ✅ 完成 | 注册和调用可用 |
| Tasks API | ✅ 完成 | `tasks/get/list/result/cancel` 可用 |
| OAuth/DNS 保护 | ✅ 完成 | DNS 重绑定保护 + OAuth 2.1 认证 |
| Sampling/Elicitation | ❌ 未开始 | - |

## 详细功能对比

| 功能 | TypeScript 能力描述 | Rust 状态 |
| --- | --- | --- |
| Stdio 传输（客户端/服务器） | 默认 stdio 传输与测试覆盖 | ✅ 已完成 |
| Streamable HTTP 传输 | HTTP+SSE/JSON 响应、会话/重连/resumption token | ✅ 已完成（axum 集成、SSE 流、双向推送、Last-Event-ID 回放） |
| HTTP+SSE 兼容传输 | 旧版 SSE 兼容（含 fallback 客户端） | ✅ 已完成（服务端 + 客户端） |
| WebSocket 传输 | `websocket.ts` 客户端传输实现 | ✅ 已完成（服务端 + 客户端） |
| DNS 重绑定保护 | `createMcpExpressApp` 自动挂载 host 校验 | ✅ 已完成（axum 中间件） |
| OAuth 授权路由（服务端） | 授权/令牌/注册/撤销/元数据路由及提供者 | ✅ 已完成（RFC 8414/9728/7591/7009） |
| OAuth 客户端认证 | Streamable HTTP 客户端 `authProvider` 处理 token/刷新 | ✅ 已完成（PKCE + Token 刷新） |
| Tools 注册/调用 | 注册工具、list/call、输出 schema 校验 | ✅ 已完成 |
| Resources 注册 | 注册资源/模板、list/read | ✅ 已完成 |
| Prompts 注册 | 注册 prompt、list/get | ✅ 已完成 |
| ResourceLink / 大资源引用 | 工具返回 `resource_link` 内容类型 | ✅ 已完成 |
| Prompt/Resource completions | 参数补全能力 | ❌ 未完成 |
| Logging setLevel | `logging/setLevel` 请求处理与客户端校验 | ✅ 已完成 |
| list_changed 通知 | tools/prompts/resources list changed + debounce 刷新 | ✅ 已完成 |
| Roots 能力 | `roots/list` 与 list_changed 支持 | ⚠️ 部分完成 |
| Sampling `createMessage` | 服务器请求客户端采样 | ❌ 未完成 |
| 表单/URL elicitation | `elicitation/create` 表单/URL 模式 | ❌ 未完成 |
| 实验性任务工具 | `.experimental.tasks` 注册 task 工具 | ⚠️ 部分完成 |
| 任务 API | `tasks/get/list/result/cancel` 与存储 | ✅ 已完成 |
| Completion 工具 | `completion/complete`（提示/资源） | ❌ 未完成 |

## 传输层详情

### Stdio 传输 ✅

- 客户端：`StdioClientTransport`
- 服务端：通过 stdin/stdout 通信
- 支持子进程管理

### HTTP/SSE 传输 ✅

详见 [HTTP/SSE 传输文档](./http-sse.md)。

- 真正的 SSE 长连接流
- 双向消息推送
- Last-Event-ID 断线重连回放
- CORS 支持
- axum 框架集成

### WebSocket 传输 ✅

详见 [WebSocket 传输文档](./websocket.md)。

- 全双工 WebSocket 通信
- MCP 子协议协商
- 服务端 + 客户端实现
- CORS 支持
- axum 框架集成

### 旧版 HTTP+SSE 兼容传输 ✅

详见 [旧版 SSE 传输文档](./legacy-sse.md)。

- 支持协议版本 2024-11-05
- 通过 URL 查询参数传递 session ID
- 发送 `endpoint` 事件
- 服务端 + 客户端实现
- 可与 Streamable HTTP 同时运行

## 安全与认证 ✅

### DNS 重绑定保护

DNS 重绑定保护通过验证 Host 头来防止恶意网站访问本地服务器。

**服务端使用示例：**

```rust
use mcp_server::http::{
    host_header_validation, localhost_host_validation, DnsProtectionConfig,
};

// 仅允许 localhost
let router = Router::new()
    .route("/mcp", post(handle_mcp))
    .layer(localhost_host_validation());

// 自定义允许的主机名
let config = DnsProtectionConfig::new(["localhost", "127.0.0.1", "example.com"]);
let router = Router::new()
    .route("/mcp", post(handle_mcp))
    .layer(host_header_validation(config));
```

**通过 `AxumHandlerConfig` 启用：**

```rust
let config = AxumHandlerConfig {
    enable_dns_rebinding_protection: true,
    dns_protection_config: None, // 使用默认 localhost 配置
    ..Default::default()
};
```

### OAuth 2.1 认证

完整实现 OAuth 2.1 授权流程，支持：

- RFC 8414: 授权服务器元数据发现
- RFC 9728: 受保护资源元数据
- RFC 7591: 动态客户端注册
- RFC 7009: Token 撤销
- RFC 7636: PKCE (S256)

**服务端 OAuth 路由：**

```rust
use mcp_server::auth::{create_oauth_router, OAuthRouterOptions};

let options = OAuthRouterOptions::new("https://auth.example.com")
    .with_scopes(vec!["read".to_string(), "write".to_string()]);

let oauth_router = create_oauth_router(provider, options);

let app = Router::new()
    .merge(oauth_router)
    .merge(mcp_router);
```

**服务端 Bearer 认证中间件：**

```rust
use mcp_server::auth::middleware::{BearerAuthLayer, BearerAuthOptions};

let options = BearerAuthOptions::new()
    .with_scopes(vec!["read".to_string()]);

let router = Router::new()
    .route("/mcp", post(handle_mcp))
    .layer(BearerAuthLayer::with_options(verifier, options));
```

**客户端 OAuth 认证：**

```rust
use mcp_client::auth::{auth, AuthOptions, InMemoryOAuthClientProvider};
use mcp_core::auth::OAuthClientMetadata;

let metadata = OAuthClientMetadata {
    redirect_uris: vec!["http://localhost:8080/callback".to_string()],
    client_name: Some("My App".to_string()),
    ..Default::default()
};

let provider = InMemoryOAuthClientProvider::new(
    Some("http://localhost:8080/callback".to_string()),
    metadata,
);

let result = auth(&provider, AuthOptions::new("https://api.example.com")).await?;

// 使用 HttpClientConfig 集成
let config = HttpClientConfig::new("https://api.example.com")
    .auth_provider(Arc::new(provider));
```

## 后续完善方向

1. **MCP 能力补齐**
   - sampling、elicitation（表单+URL）
   - 实验性任务流式 helper
   - Roots 服务端支持
   - Completions 支持
