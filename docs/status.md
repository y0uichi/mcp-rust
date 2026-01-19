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
| OAuth/DNS 保护 | ❌ 未开始 | - |
| Sampling/Elicitation | ❌ 未开始 | - |

## 详细功能对比

| 功能 | TypeScript 能力描述 | Rust 状态 |
| --- | --- | --- |
| Stdio 传输（客户端/服务器） | 默认 stdio 传输与测试覆盖 | ✅ 已完成 |
| Streamable HTTP 传输 | HTTP+SSE/JSON 响应、会话/重连/resumption token | ✅ 已完成（axum 集成、SSE 流、双向推送、Last-Event-ID 回放） |
| HTTP+SSE 兼容传输 | 旧版 SSE 兼容（含 fallback 客户端） | ✅ 已完成（服务端 + 客户端） |
| WebSocket 传输 | `websocket.ts` 客户端传输实现 | ✅ 已完成（服务端 + 客户端） |
| DNS 重绑定保护 | `createMcpExpressApp` 自动挂载 host 校验 | ❌ 未完成 |
| OAuth 授权路由（服务端） | 授权/令牌/注册/撤销/元数据路由及提供者 | ❌ 未完成 |
| OAuth 客户端认证 | Streamable HTTP 客户端 `authProvider` 处理 token/刷新 | ❌ 未完成 |
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

## 后续完善方向

1. **安全与认证**
   - 添加 DNS 重绑定保护
   - 实现 OAuth 授权流程

2. **MCP 能力补齐**
   - sampling、elicitation（表单+URL）
   - 实验性任务流式 helper
   - Roots 服务端支持
   - Completions 支持
