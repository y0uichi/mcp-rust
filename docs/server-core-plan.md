# Rust MCP Server/Core 方案（参考 TypeScript 实现）

## 参考实现位置（TypeScript SDK）
- core 协议与类型：`/Users/apple/dev/typescript-sdk/packages/core/src/shared/protocol.ts`
- 核心类型与版本：`/Users/apple/dev/typescript-sdk/packages/core/src/types/types.ts`
- Server 低层封装：`/Users/apple/dev/typescript-sdk/packages/server/src/server/server.ts`
- McpServer 高层封装：`/Users/apple/dev/typescript-sdk/packages/server/src/server/mcp.ts`

## 目标
- 在 `mcp_core` 中补齐协议层能力与类型对齐（版本、capabilities、tasks、通知与请求处理）。
- 在 `mcp_server` 中提供与 TS `Server`/`McpServer` 等价的两层 API：底层可自定义 handler，高层提供 tools/resources/prompts 的注册与默认 handler。
- 保持 Rust 代码“一个类型一个文件”的组织方式，并将测试文件独立放置。

## 分层设计
1) **core（mcp_core）**
- `Protocol`：负责 JSON-RPC 包装、能力检查、任务扩展、超时/取消、请求/通知路由。
- `types`：版本号、协议常量、能力结构、请求/通知/结果类型、错误码。
- `schema`：统一 JSON Schema 校验器接口，支持工具输入/输出、elicitation 响应校验。

2) **server（mcp_server）**
- `Server`：围绕 `Protocol` 的低层封装，负责初始化流程、capabilities 注册、logging level 处理、oninitialized 回调等。
- `McpServer`：更高层 API，维护 tool/resource/prompt 注册表并注册默认 handler。

## 核心能力对齐要点（core）
- **协议版本**：对齐 `LATEST_PROTOCOL_VERSION` 与 `SUPPORTED_PROTOCOL_VERSIONS`，提供协商默认版本。
- **JSON-RPC 类型**：Request/Notification/Result 与错误码枚举；将 `RequestId`、`_meta`、`progressToken`、`related-task` 纳入结构。
- **tasks 扩展**：支持 task-augmented request；核心需要解析 `task` 字段并提供 task store/queue 能力接口。
- **capabilities**：实现 `mergeCapabilities` 与严格能力检查（`enforceStrictCapabilities`）。
- **超时与取消**：Protocol 层提供 request timeout、abort 处理的统一入口（对应 TS `RequestOptions`）。

## Server（低层）实现要点
- **初始化流程**：`initialize` 请求处理、校验 `protocolVersion`、缓存 client capabilities/versions、返回 server capabilities 与 instructions。
- **capabilities 注册**：连接前允许 merge，连接后禁止（与 TS 一致）。
- **日志等级**：如果开启 logging capability，支持 `logging/setLevel` 并按 sessionId 记录当前等级。
- **安全处理**：统一返回 `McpError`，并在 request handler 中统一进行 schema 校验。

## McpServer（高层）实现要点
- **注册表**：tools/resources/prompts/ resourceTemplates 统一存储；每类一个结构体文件。
- **默认 handler**：自动注册 list/call/read/get 等方法，暴露 JSON Schema（输入/输出）。
- **tool 任务支持**：支持 taskSupport = required/optional 的分支逻辑；可选自动轮询。
- **能力声明**：注册 tool/resource/prompt 时自动合并到 server capabilities。

## 文件组织建议（Rust）
- `core/src/protocol/mod.rs` 拆分：`protocol.rs` 只保留运行时，`request.rs`/`response.rs`/`options.rs` 分文件。
- `core/src/types/`：每个类型一个文件（例如 `capabilities.rs`, `version.rs`, `errors.rs`, `jsonrpc.rs`, `tasks.rs`）。
- `server/src/server/`：`server.rs`、`mcp_server.rs`、`registries/`（tools/resources/prompts）。
- `server/tests/`：每类能力单独测试文件，避免内联测试。

## 迁移步骤（建议）
1) **core 类型补齐**：先对齐版本、错误码、JSON-RPC 基础类型、capabilities 结构。
2) **Protocol 扩展**：加入 request options（超时/取消）、progress、task augmentation 支持。
3) **Server 低层**：实现 initialize 流程与 logging level 支持，能力注册约束。
4) **McpServer 高层**：实现注册表 + 默认 handler（tools/resources/prompts）。
5) **任务与列表通知**：实现 listChanged 通知与 task polling。
6) **测试**：为 initialize、capabilities、tools/resources/prompts、tasks 分别建立独立测试文件。

## 与现有 Rust 代码的对齐点
- 当前 `core/src/protocol.rs` 仅支持简单 request handler，需要扩展为可配置 options 和能力验证。
- `core/src/types.rs` 需要拆分并补齐 MCP 2025-11-25 的能力与 task 结构。
- server/client 目前为最小演示，后续按上述分层补齐即可。

## 产出物（最终文件）
- `core/src/types/` 全量类型定义
- `core/src/protocol/` 运行时 + options + task 支持
- `server/src/server/server.rs` 与 `server/src/server/mcp_server.rs`
- `server/tests/` 下的初始化、能力、工具、资源、任务测试
