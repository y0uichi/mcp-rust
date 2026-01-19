## TypeScript SDK vs Rust 工作空间差异

以下对比基于 `typescript-sdk` 和当前的 Rust 目录结构，聚焦尚未在 Rust 中实现的关键能力。

### 1. 传输层与部署

- **Streamable HTTP / SSE 传输**：TypeScript 完整实现了 Streamable HTTP 客户端与服务器传输（`packages/server/src/server/streamableHttp.ts`、`packages/client/src/client/streamableHttp.ts`），包括 SSE、会话 ID、重连策略与 resumption token。Rust 现已实现基础的 HTTP/SSE 传输（`client/src/http/`、`server/src/http/`），包括：
  - `HttpClientTransport`：HTTP POST 发送消息 + SSE 接收消息、会话管理、指数退避重连策略
  - `HttpServerHandler`：框架无关的 HTTP 处理器，支持 POST/GET/DELETE 请求
  - `SessionManager`：服务端会话管理，支持 resumption token
  - `SseWriter`/`SseParser`：SSE 事件序列化与解析
- **DNS 重绑定保护 & Express 集成**：TypeScript 提供 `createMcpExpressApp`（`packages/server/src/server/express.ts`）自动添加 DNS 保护中间件，并在文档中说明（`docs/server.md`）如何部署；Rust 端尚未有 web 框架集成或相关防护说明。

### 2. 身份认证与授权

- **OAuth 授权服务器**：TypeScript 针对 OAuth 提供了客户端/服务端工具链，包含 `packages/client/src/client/auth.ts` 中的 OAuth 客户端接口和 `packages/server/src/server/auth/router.ts` 的授权/token/router 集成，以及 `docs/client.md` 中的示例；Rust 当前只通过 stdio 客户端/服务端通信，没有 OAuth 提供者、处理令牌的 middleware 或在 docs 中提及。

- **客户端认证策略**：TypeScript 的 Streamable HTTP 客户端（`packages/client/src/client/streamableHttp.ts#L88`）支持 OAuth 认证提供者、token 刷新与未授权处理，Rust 端还未实现类似机制。

### 3. 采样、elicitation 与实验性任务

- **采样请求与校验**：TypeScript 服务器在 `packages/server/src/server/server.ts#L482-L555` 提供 `createMessage` 方法用于向支持 sampling 的客户端请求生成内容，并在客户端（`packages/client/src/client/client.ts#L687-L718`）校验 `sampling/createMessage` 权限。Rust 目前没有 `createMessage` 或 sampling 调用路径。
- **表单/URL elicitation**：TypeScript 实现了 `elicitation/create` 请求，并在 docs 中专门说明两种模式（`docs/capabilities.md#L19-L48`）；Rust 目前未看到对应请求处理或能力检测。
- **实验性任务 API**：TypeScript 在 `packages/server/src/experimental/tasks/mcp-server.ts`、`packages/client/src/experimental/tasks/client.ts` 提供 `.experimental.tasks` 命名空间用于注册/调用任务工具，并在 docs 中列出用途（`docs/capabilities.md#L49-L79`）。Rust 虽在 `server/src/server/server.rs` 注册了基本的 `tasks/get/list/result/cancel` 处理，但缺少 `.experimental` 注册器、工具调用流程与客户端 streaming helpers。

### 4. 资源/提示与通知补全

- TypeScript 文档（`docs/server.md#L96-L200`）详细讲解通过 `registerTool`、`registerResource`、`registerPrompt` 构建工具/资源/提示及支持 completions、ResourceLink 等扩展；Rust 的 `McpServer` 目前只实现最基本的工具/资源/提示注册与 `list`/`call`/`read` 请求，没有提到 completions、递归 resource_link 或 prompt metadata 的 JS SDK 中的交互模式。

### 建议的推进方向

1. ~~先为 Rust 加入 HTTP/SSE 传输~~ ✅ 已完成。下一步：添加 DNS/OAuth 相关部署工具，确保服务端可以在网络环境中与客户端互通并受保护。
2. 再补齐语言层面的 sampling、elicitation（表单+URL）和实验任务支持，参照 TypeScript 对请求、能力检查与客户端 helper 的设计。
3. 补充 docs（如新增 `docs/typescript-comparison.md`）并与现有 `McpServer`/`Client` 接口同步解释新的能力。

### 功能状态概览

| 功能 | TypeScript 能力描述 | Rust 状态 |
| --- | --- | --- |
| Stdio 传输（客户端/服务器） | 默认 stdio 传输与测试覆盖 | 已完成 |
| Streamable HTTP 传输 | HTTP+SSE/JSON 响应、会话/重连/resumption token | 已完成 |
| HTTP+SSE 兼容传输 | 旧版 SSE 兼容（含 fallback 客户端） | 未完成 |
| WebSocket 传输（客户端） | `websocket.ts` 客户端传输实现 | 未完成 |
| DNS 重绑定保护 | `createMcpExpressApp` 自动挂载 host 校验 | 未完成 |
| OAuth 授权路由（服务端） | 授权/令牌/注册/撤销/元数据路由及提供者 | 未完成 |
| OAuth 客户端认证 | Streamable HTTP 客户端 `authProvider` 处理 token/刷新 | 未完成 |
| Tools 注册/调用 | 注册工具、list/call、输出 schema 校验 | 已完成 |
| Resources 注册 | 注册资源/模板、list/read | 已完成 |
| Prompts 注册 | 注册 prompt、list/get | 已完成 |
| ResourceLink / 大资源引用 | 工具返回 `resource_link` 内容类型 | 未完成 |
| Prompt/Resource completions | 参数补全能力 | 未完成 |
| Logging setLevel | `logging/setLevel` 请求处理与客户端校验 | 已完成 |
| list_changed 通知 | tools/prompts/resources list changed + debounce 刷新 | 已完成 |
| Roots 能力 | `roots/list` 与 list_changed 支持 | 部分完成（客户端已实现 roots/list 响应，缺 server helper 和 list_changed） |
| Sampling `createMessage` | 服务器请求客户端采样，校验工具结果匹配 | 未完成 |
| 表单/URL elicitation | `elicitation/create` 表单/URL 模式与默认处理 | 未完成 |
| 实验性任务工具 | `.experimental.tasks` 注册 task 工具、流式任务状态 | 部分完成（有 TaskStore，但缺注册/流式 helper） |
| 任务 API | `tasks/get/list/result/cancel` 与存储 | 已完成 |
| Completion 工具 | `completion/complete`（提示/资源） | 未完成 |

### Roots 能力说明（易读版）

Roots = 客户端允许服务器访问的“根目录”列表（通常是 `file://` 路径，包含可选名称/元数据）。这是 MCP 里用来表达“可操作文件范围”的核心概念：服务器不知道用户的文件系统，必须由客户端主动告知允许的根，再在这些根内执行文件浏览、读取等操作。服务器通过 `roots/list` 来询问这些目录，用来限定后续文件/资源操作的范围，避免越权。典型流程：
- 连接完成后，服务器先发 `roots/list`，拿到客户端授权的 file:// 前缀。
- 之后的资源读取/工具操作应限制在这些根内（如列目录、读取文件）。
- 若客户端本地允许路径变化，可通过 `notifications/roots/list_changed` 通知服务器刷新。

现状：
- **客户端**：用 `ClientOptions::with_roots([...])` 传入 roots，客户端会在收到 `roots/list` 请求时把这份列表返回。

还缺少：
- **服务端**：没有 roots 管理/缓存，也没有 `roots/list_changed` 通知。
- **示例/文档**：没有示例展示 roots 的实际用法（文件系统过滤等），HTTP/SSE 传输也未接 roots 通知。

后续建议（按优先级）：
1. 服务端增加 roots registry 与 `roots/list_changed` 通知，并在 capability 校验中启用。
2. 客户端如需支持 roots 变化，可扩展 list_changed 订阅/刷新。
3. 增加示例：基于文件系统的 roots 流程，覆盖 stdio 和 HTTP/SSE。

示例（客户端侧）：
```rust
use mcp_client::{
    client::ClientOptions,
    client::Root,
};

// 声明可访问的根目录列表
let roots = vec![
    Root::new("file:///Users/apple/dev/projectA"),
    Root::new("file:///tmp/workspace"),
];

// 构建客户端时注入 roots
let options = ClientOptions::new("demo-client")
    .with_roots(roots);
// 连接后，当服务器发起 `roots/list` 请求时，会返回上述列表
```
