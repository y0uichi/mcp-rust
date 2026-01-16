# Rust 客户端重写计划
- **目标**：逐步将 `packages/client/src/client/client.ts` 的核心逻辑（协议/transport/工具/能力/任务）迁移为 Rust 的 `mcp_client::Client`，并保持与 `mcp_core` 共享的基础结构。
- **阶段 1 — 梳理差异与复用点**
  1. 阅读 TS `client.ts`、`experimental/tasks/client.ts` 及 `@modelcontextprotocol/core` 中的 `Protocol`、schema、validator、transport 等导出，列出必须复刻的接口。
  2. 对照现有 Rust 组件（`mcp_core::{Protocol, types, stdio::ReadBuffer}`、`client::stdio::StdioClientTransport` 等），确认可以复用的部分与缺失功能。
  3. 明确第一阶段范围：先复现认证/transport/请求流动，后续再补能力/任务/elicitation。
- **阶段 1 进度报告**
  1. **TS 依赖与核心概念**
     - `Client` 封装了 `Protocol`（handlers、schema validation）、`Transport`（stdio/streamable HTTP/SSE/WS）、`Capabilities`（elicitation/task/tool metadata）、`Tools/Prompts/Resources` 列表、`ExperimentalClientTasks`。`Core` package 提供 `CallToolResultSchema`/`ListToolsResultSchema`/`ErrorCode` 等常量。
     - `client.ts` 中融合了 `AjvJsonSchemaValidator`、`ProtocolOptions`（transport、logger、auth），并按需在 `callTool`、`listTools` 等方法里调用 `Protocol` 进行 JSON-RPC 请求，所有 responses 通过 `Transport` 发送/接收。
  2. **现有 Rust 结构匹配**
     - `mcp_core::Protocol`（`core/src/protocol.rs`）已提供 handler 注册 + request validation，`core::types` 包含 Request/Result/Notification 结构；`core/src/stdio` 提供 JSON-RPC buffer/serialize 工具；
     - `mcp_client::stdio::StdioClientTransport`（`client/src/stdio/transport.rs`）实现了 `mcp_core::stdio::Transport` trait，提供 spawn/stdio 交互、env filtering、stderr relaying。
     - 没有 yet Rust counterpart for `Capabilities`, `ExperimentalClientTasks` schema, or `streamableHttp` transport.
  3. **阶段 1 输出**
     - 先复现 `Client` 的启动/handshake/transport wiring：Rust 端需要一个 `ClientOptions` + `Client` struct，包含 `Protocol` 实例、`Transport` trait 对象、`capabilities` metadata。
     - 搭建 `call_tool`, `list_tools` 等方法时可先只依赖 `serde_json::Value` + `mcp_core::Protocol`，后续再引入验证 schema。
     - 将 `experimental/tasks` 行为延迟到阶段 4，但记录所需 schema（task creation/result、notification names），以便之后实现 `ExperimentalClientTasks` 模块。
- **阶段 2 — 设计 Rust Client 架构**
  1. 定义 `ClientOptions`、`ClientCapabilities`、`ProtocolOptions` 等类型，映射 TS 抽象，并借助 `serde_json::Value` 管理 schema。
  2. 继续复用 `mcp_core::stdio::Transport` trait，允许 `Client` 接受任意实现（目前 stdio transport 即可）。
  3. 建立 `Client` 内部的 `Protocol` + handler 注册流程，并规划 `call_tool`、`list_tools/prompts/resources` 等高阶方法。
- **阶段 3 — 实现核心客户端逻辑**
  1. 搭建 `mcp_client::Client` 结构，包含 `protocol`、`transport`、`options`、`capabilities` 等字段。
  2. 实现 `call_tool`、`list_*`、`get_prompt`、`experimental/tasks` 入口，复用 `ClientOptions` 中的 `jsonSchemaValidator` 等扩展点。
  3. 移植 `applyElicitationDefaults`、`getSupportedElicitationModes`、`mergeCapabilities` 之类的工具函数。
- **阶段 4 — 拓展任务与资源支持**
  1. 把 `Tool`/`Prompt`/`Resource` 等 schema 放到 `mcp_core::schema`，并使 `Client` 能够解析/校验这些结构。
  2. 添加 `ExperimentalClientTasks` 模块，提供 `call_tool_stream`、`get_task` 等 TS 等价 API。
  3. 设计 `ListChangedHandler` 回调注册机制，允许 client 响应服务器推送。
- **阶段 5 — 测试与示例**
  1. 为所有 Client 方法补充单元测试，包括 `Protocol` 交互、transport 回调、schema 校验。
  2. 新建 stdio/streamable-http 示例，演示 Rust client + Rust server/TS server 协作。
  3. 更新 `docs/` 中的使用指南，说明如何依次构建 transport、能力、任务。
- **阶段 6 — 进一步扩展**
  1. 增加 HTTP/SSE transport，仿 TS `streamableHttp.ts`。
  2. 实现 OAuth helpers（Token Provider、auth middleware）。
  3. 编写 cross-language 集成测试（Rust client ↔ TS server，反之亦然）。
