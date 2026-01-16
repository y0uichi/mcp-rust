# Rust 客户端重写计划（基于 TS Client 实现）
- **目标**：对齐 TS `packages/client/src/client/client.ts` 与 `experimental/tasks/client.ts` 的行为，将核心客户端能力迁移到 Rust `mcp_client::Client`，并复用 `mcp_core` 的协议与类型。

## 清单
### 阶段 1 — 架构与类型落地
- [ ] 拆分 `ClientOptions` 类型定义（独立文件，包含协议/transport/options 合并策略）。
- [ ] 拆分 `ClientCapabilities` 类型定义（独立文件，对齐 TS capability 结构）。
- [ ] 拆分 `ListChangedHandlers` 与 `ListChangedOptions` 类型定义（独立文件）。
- [ ] 定义 `JsonSchemaValidator` trait + `AjvJsonSchemaValidator` 等价接口占位。
- [ ] `Client::new` 初始化：保存 `client_info`、默认 capabilities、默认 validator。
- [ ] `Client::connect` 增加 `initialize` 请求与结果校验。
- [ ] 保存 `serverInfo`/`capabilities`/`instructions` 字段与 getter。
- [ ] 初始化后发送 `notifications/initialized`。
- [ ] `registerCapabilities`：仅允许连接前调用，合并逻辑对齐 TS `mergeCapabilities`。
- [ ] `assertCapabilityForMethod`：按 method 分类检查 server capability。
- [ ] `assertNotificationCapability`：检查 client capability（roots/list_changed）。
- [ ] `assertRequestHandlerCapability`：检查 client handler capability（sampling/elicitation/roots/tasks）。

### 阶段 2 — 工具与列表体系
- [ ] `list_tools` 返回后缓存 tool 元数据（outputSchema/任务支持）。
- [ ] outputSchema 校验器缓存结构（Map<tool, validator>）。
- [ ] `isToolTask` 与 `isToolTaskRequired` 实现。
- [ ] `call_tool` 校验：structuredContent 必须匹配 outputSchema。
- [ ] required-task 工具：阻止非 streaming 执行路径。
- [ ] listChanged 配置结构体：`autoRefresh` + `debounceMs`。
- [ ] listChanged handler 注册：tools/prompts/resources 的通知绑定。
- [ ] debounce 逻辑与刷新回调实现。

### 阶段 3 — 任务与流式支持
- [ ] `Protocol` 增加 `request_stream` 基础能力。
- [ ] `Client::request_stream` 暴露 response 流接口。
- [ ] `ExperimentalClientTasks` 模块入口与结构体定义。
- [ ] `call_tool_stream` 实现（自动 task 参数注入）。
- [ ] 流式结果的 outputSchema 校验。
- [ ] `get_task`/`get_task_result`/`list_tasks`/`cancel_task` 直通协议方法。
- [ ] `assertTaskCapability` 与 `assertTaskHandlerCapability` 对齐 TS 逻辑。

### 阶段 4 — elicitation/sampling 与默认值
- [ ] `set_request_handler` 包装：识别 `elicitation/create`。
- [ ] `set_request_handler` 包装：识别 `sampling/createMessage`。
- [ ] `applyElicitationDefaults`：递归默认值应用（object/anyOf/oneOf）。
- [ ] `getSupportedElicitationModes`：支持 form/url 模式判断。
- [ ] task result 兼容：`CreateTaskResult` 与 `ElicitResult`/`CreateMessageResult` 分支校验。

### 阶段 5 — transport 扩展与测试
- [ ] HTTP transport 设计（streamable HTTP headers + protocolVersion）。
- [ ] SSE transport 实现（event stream + reconnect 支持）。
- [ ] WebSocket transport 实现（双向流）。
- [ ] listChanged 机制测试（autoRefresh/去抖）。
- [ ] callTool outputSchema 校验测试。
- [ ] request_stream/任务流测试。
- [ ] capability 断言测试（请求/通知/handler）。
- [ ] stdio 示例补充（基础 initialize + listTools + callTool）。
- [ ] HTTP 示例补充（streamable HTTP client + server）。

## TS Client 关键行为清单（用于 Rust 对照）
- **连接与握手**：`connect()` 触发 `initialize` 请求；校验 `protocolVersion`；保存 `serverInfo`、`capabilities`、`instructions`；必要时调用 `transport.setProtocolVersion`；发送 `notifications/initialized`。
- **能力与断言**：`registerCapabilities` 仅在未连接时允许；按 method 断言 server/client capability（logging/prompts/resources/tools/completions/tasks/elicitation/sampling/roots）。
- **listChanged 机制**：初始化后根据 server capabilities 配置通知 handler，支持 `autoRefresh` + `debounceMs`；收到通知时自动刷新 tools/prompts/resources 列表。
- **工具调用校验**：`listTools()` 后缓存 `outputSchema` 校验器与 task 支持信息；`callTool()` 对结构化输出做 JSON Schema 校验；required-task 工具强制走 streaming API。
- **请求处理增强**：`setRequestHandler` 针对 `elicitation/create`、`sampling/createMessage` 做 schema 校验与 task result 兼容；`elicitation` 支持默认值应用。
- **Experimental tasks**：`callToolStream()` 通过 `requestStream` 返回任务流；`getTask`/`getTaskResult`/`listTasks`/`cancelTask` 直通协议方法；流式结果同样校验工具输出。

## Rust 现状对照
- **可复用**：`mcp_core::Protocol`、`core::types`、`core::stdio`；`client::stdio::StdioClientTransport`。
- **缺失点**：`ClientCapabilities` 合并、listChanged 机制、JSON Schema 校验器封装、工具输出校验缓存、任务流与 `ExperimentalClientTasks`、HTTP/SSE/WS transport。

## 重写分阶段计划
### 阶段 1 — 架构与类型落地
1. **类型建模**：新增 `ClientOptions`、`ClientCapabilities`、`ListChangedHandlers`、`JsonSchemaValidator` 等类型，与 TS 对齐；按“一类型一文件”拆分。
2. **基础连接**：在 `Client::connect` 中实现 `initialize` 流程、协议版本校验、`serverInfo`/`instructions` 保存。
3. **能力断言**：为 requests/notifications/handlers 增加 capability 校验（参考 TS `assertCapabilityForMethod`/`assertNotificationCapability`）。

### 阶段 2 — 工具与列表体系
1. **listTools 缓存**：引入工具元数据缓存（`outputSchema` 校验器、task 支持标记）。
2. **callTool 校验**：在 `call_tool` 中对结构化输出进行 JSON Schema 校验；required-task 工具强制走任务流。
3. **listChanged 处理**：按 tools/prompts/resources 订阅通知，支持 `autoRefresh` + `debounceMs`。

### 阶段 3 — 任务与流式支持
1. **requestStream**：在 `Protocol`/client 侧增加 stream API，输出 `ResponseMessage` 流。
2. **ExperimentalClientTasks**：实现 `call_tool_stream`/`get_task`/`get_task_result`/`list_tasks`/`cancel_task`，并复用工具输出校验。
3. **任务能力断言**：匹配 TS 的 `assertTaskCapability`/`assertTaskHandlerCapability` 行为。

### 阶段 4 —  elicitation/sampling 与默认值
1. **handler 包装**：为 `elicitation/create`、`sampling/createMessage` 提供 wrapper 校验逻辑。
2. **默认值应用**：实现 `applyElicitationDefaults` + `getSupportedElicitationModes`，支持表单默认值回填。

### 阶段 5 — transport 扩展与测试
1. **Transport 扩展**：实现 streamable HTTP/SSE/WS transport，对齐 TS 客户端能力。
2. **测试体系**：按“测试文件独立放置”，补齐 listChanged、callTool 校验、任务流、能力断言的单测。
3. **示例与文档**：新增 Rust client 示例与使用文档（stdio + HTTP）。
