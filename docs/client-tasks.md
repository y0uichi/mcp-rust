# Rust 客户端重写任务清单（详细说明）

本文档按阶段列出任务，并为每一项提供方案说明与文档化描述，便于实施与验收。

## 阶段 1 — 架构与类型落地

- [ ] 拆分 `ClientOptions` 类型定义（独立文件，包含协议/transport/options 合并策略）。
  方案说明：在 `client/src/options/` 下新增 `client_options.rs`，将连接相关配置（logger、request timeout、transport hooks）与 client 扩展配置（capabilities、listChanged、json schema validator）集中管理，并提供构造与默认值实现。对齐 TS `ClientOptions` 的结构层级，避免与 `ProtocolOptions` 混杂。
  文档说明：在模块 doc 中说明字段来源与默认策略（未指定 validator 使用默认实现；listChanged 在初始化后延迟生效）。

- [ ] 拆分 `ClientCapabilities` 类型定义（独立文件，对齐 TS capability 结构）。
  方案说明：新增 `client_capabilities.rs`，按 TS 结构定义 `logging/prompts/resources/tools/completions/roots/tasks/elicitation/sampling` 等字段，字段尽量使用 `Option<...>` 以匹配可选语义；合并逻辑与 `mergeCapabilities` 保持一致。
  文档说明：说明每个 capability 的开关语义，以及对对应请求/通知的影响（例如 roots.listChanged 影响 `notifications/roots/list_changed`）。

- [ ] 拆分 `ListChangedHandlers` 与 `ListChangedOptions` 类型定义（独立文件）。
  方案说明：新增 `list_changed.rs`，定义 `ListChangedOptions { auto_refresh, debounce_ms, on_changed }` 与 `ListChangedHandlers { tools, prompts, resources }`，并提供校验逻辑（autoRefresh 与 debounce 的默认行为）。
  文档说明：描述 listChanged 只在 server capability 支持时启用，且在 connect 初始化后才注册。

- [ ] 定义 `JsonSchemaValidator` trait + `AjvJsonSchemaValidator` 等价接口占位。
  方案说明：新增 `json_schema_validator.rs`，定义 `JsonSchemaValidator` trait，方法包括 `get_validator(schema) -> ValidatorFn`；提供一个占位实现（比如返回始终 valid 的 validator），后续可接入具体库。
  文档说明：说明 validator 用途仅限工具 outputSchema 校验，不影响基础 JSON-RPC 流程。

- [ ] `Client::new` 初始化：保存 `client_info`、默认 capabilities、默认 validator。
  方案说明：在 `client.rs` 中构造 `Client` 时初始化字段，包括 `client_info`、`capabilities`、`validator`、缓存结构与 listChanged 待配置项；默认 validator 使用 `AjvJsonSchemaValidator` 等价实现。
  文档说明：说明 `Client::new` 不建立连接，也不会触发任何网络行为。

- [ ] `Client::connect` 增加 `initialize` 请求与结果校验。
  方案说明：在 `connect` 中调用 protocol `request` 发送 `initialize`；校验 `protocolVersion` 与结果 schema；失败时关闭 transport 并返回错误。
  文档说明：列出 connect 的握手步骤与失败处理路径（包含断线与错误返回）。

- [ ] 保存 `serverInfo`/`capabilities`/`instructions` 字段与 getter。
  方案说明：在 `Client` 结构体中新增字段保存初始化结果；提供 `get_server_capabilities`、`get_server_version`、`get_instructions` getter。
  文档说明：说明这些字段仅在 initialize 成功后可用，否则为 `None`。

- [ ] 初始化后发送 `notifications/initialized`。
  方案说明：在 initialize 成功后调用 `notification` 发送 `notifications/initialized`；若失败则返回 error。
  文档说明：解释该通知用于告知 server 客户端完成初始化，与 TS 行为一致。

- [ ] `registerCapabilities`：仅允许连接前调用，合并逻辑对齐 TS `mergeCapabilities`。
  方案说明：提供 `register_capabilities`，在已有 transport 时拒绝调用；合并逻辑采用字段级合并（非覆盖式）。
  文档说明：说明该方法用于扩展 client 声明能力，必须在 connect 前调用。

- [ ] `assertCapabilityForMethod`：按 method 分类检查 server capability。
  方案说明：在发起请求前，根据 method 分类检查 server capabilities（logging/prompts/resources/tools/completions/tasks）；不满足则返回错误。
  文档说明：提供 method → capability 的映射表，作为行为约束说明。

- [ ] `assertNotificationCapability`：检查 client capability（roots/list_changed）。
  方案说明：发送通知前检查 client 是否声明对应能力（目前重点是 roots.listChanged），否则拒绝发送。
  文档说明：说明这是 client 自身约束，防止发送未声明支持的通知。

- [ ] `assertRequestHandlerCapability`：检查 client handler capability（sampling/elicitation/roots/tasks）。
  方案说明：在注册 request handler 时检查 client capabilities；对于 `elicitation/create` 与 `sampling/createMessage` 等 handler，若未声明能力则报错。
  文档说明：说明该检查在 handler 注册时执行，避免运行时的隐式失败。

## 阶段 2 — 工具与列表体系

- [ ] `list_tools` 返回后缓存 tool 元数据（outputSchema/任务支持）。
  方案说明：在 `list_tools` 成功后遍历 tools，缓存每个 tool 的 `outputSchema` 与 `execution.taskSupport`。
  文档说明：说明缓存用于后续 `call_tool` 校验与 task 路由判断。

- [ ] outputSchema 校验器缓存结构（Map<tool, validator>）。
  方案说明：使用 `HashMap<String, ValidatorFn>` 持有每个 tool 的校验器，初始化/刷新时重建。
  文档说明：说明缓存的生命周期与更新时机（每次 listTools 刷新）。

- [ ] `isToolTask` 与 `isToolTaskRequired` 实现。
  方案说明：基于缓存的 taskSupport 标记实现 `is_tool_task`（required/optional）与 `is_tool_task_required`（仅 required）。
  文档说明：说明这两个判断用于非流式调用的安全检查与自动 task 注入。

- [ ] `call_tool` 校验：structuredContent 必须匹配 outputSchema。
  方案说明：当 tool 有 outputSchema 时，校验 `structuredContent` 的存在性与 schema 匹配；若 `isError` 则跳过校验。
  文档说明：说明这是与 TS 对齐的行为，确保工具输出结构化一致。

- [ ] required-task 工具：阻止非 streaming 执行路径。
  方案说明：在 `call_tool` 前检查 `is_tool_task_required`，若为 true 则直接报错并提示使用任务流。
  文档说明：说明与 TS `callTool` 的 guard 一致，避免错误执行模式。

- [ ] listChanged 配置结构体：`autoRefresh` + `debounceMs`。
  方案说明：实现默认 `autoRefresh=true`、`debounceMs=None` 的配置；提供校验避免非法值。
  文档说明：说明 listChanged 配置只描述 client 行为，不影响 server。

- [ ] listChanged handler 注册：tools/prompts/resources 的通知绑定。
  方案说明：在 initialize 之后根据 server capability 注册 notification handler；收到通知后调用对应 list API 获取新列表。
  文档说明：说明 listChanged handler 仅在 server 声明支持时启用。

- [ ] debounce 逻辑与刷新回调实现。
  方案说明：若设置 `debounceMs`，使用定时器延迟执行刷新，期间合并多次通知。
  文档说明：说明 debounce 仅影响刷新频率，不影响通知处理本身。

## 阶段 3 — 任务与流式支持

- [ ] `Protocol` 增加 `request_stream` 基础能力。
  方案说明：扩展 `Protocol`，支持返回 `ResponseMessage` 流；保证流以 result 或 error 结束。
  文档说明：说明该能力用于任务模式与长时执行流式反馈。

- [ ] `Client::request_stream` 暴露 response 流接口。
  方案说明：在 client 层对外暴露 `request_stream`，直接委托 `Protocol`。
  文档说明：说明该 API 为实验性接口，未来可能调整。

- [ ] `ExperimentalClientTasks` 模块入口与结构体定义。
  方案说明：新增 `experimental/tasks` 模块，提供 tasks 入口与客户端包装。
  文档说明：说明模块为实验性质，与 TS 对齐命名与入口方式。

- [ ] `call_tool_stream` 实现（自动 task 参数注入）。
  方案说明：当 tool 支持 task 时自动加 `task` 参数；否则保持用户显式配置优先。
  文档说明：说明 auto task 注入与 TS 行为一致，避免重复配置。

- [ ] 流式结果的 outputSchema 校验。
  方案说明：对 `result` 类型消息执行 outputSchema 校验，与 `call_tool` 行为一致；失败时 yield error。
  文档说明：说明流式校验只对最终 result 生效。

- [ ] `get_task`/`get_task_result`/`list_tasks`/`cancel_task` 直通协议方法。
  方案说明：提供轻量 wrapper，参数透传到 `Protocol` 的对应 request。
  文档说明：说明这些接口仅在 server 支持 tasks 时可用。

- [ ] `assertTaskCapability` 与 `assertTaskHandlerCapability` 对齐 TS 逻辑。
  方案说明：基于 server/client capabilities 的 `tasks.requests` 结构判断 method 是否允许。
  文档说明：说明该逻辑用于任务请求与 handler 注册的双向约束。

## 阶段 4 — elicitation/sampling 与默认值

- [ ] `set_request_handler` 包装：识别 `elicitation/create`。
  方案说明：在注册 handler 时包一层校验：校验 request schema、支持模式、任务结果类型。
  文档说明：说明此包装保证请求与结果符合 spec。

- [ ] `set_request_handler` 包装：识别 `sampling/createMessage`。
  方案说明：对 sampling 请求进行 schema 校验与 task 结果兼容处理。
  文档说明：说明 sampling handler 在 client 侧需要能力声明。

- [ ] `applyElicitationDefaults`：递归默认值应用（object/anyOf/oneOf）。
  方案说明：实现与 TS 同等逻辑，在 form 模式且接受内容时对 schema default 进行填充。
  文档说明：说明只在 client capability 声明 applyDefaults 时启用。

- [ ] `getSupportedElicitationModes`：支持 form/url 模式判断。
  方案说明：实现逻辑：未声明任何 mode 时默认支持 form；明确声明 url 时支持 url。
  文档说明：说明这是为兼容历史行为的规则。

- [ ] task result 兼容：`CreateTaskResult` 与 `ElicitResult`/`CreateMessageResult` 分支校验。
  方案说明：当请求包含 task 时，结果必须是 `CreateTaskResult`；否则使用对应 result schema 校验。
  文档说明：说明该行为与 TS 完全一致。

## 阶段 5 — transport 扩展与测试

- [ ] HTTP transport 设计（streamable HTTP headers + protocolVersion）。
  方案说明：实现 streamable HTTP 客户端 transport，支持设置 protocolVersion header 与 session 管理。
  文档说明：说明与 TS `StreamableHTTPClientTransport` 对齐。

- [ ] SSE transport 实现（event stream + reconnect 支持）。
  方案说明：实现 SSE 接收与重连策略，与 streamable HTTP 共享协议处理。
  文档说明：说明用于 server 推送与长连接场景。

- [ ] WebSocket transport 实现（双向流）。
  方案说明：实现 WS 连接、消息发送与接收；支持 sessionId 与协议版本传递。
  文档说明：说明 WS 是低延迟双向通道，功能对齐 TS `WebSocketClientTransport`。

- [ ] listChanged 机制测试（autoRefresh/去抖）。
  方案说明：使用 mock transport/handler 验证通知触发刷新、debounce 合并行为。
  文档说明：说明测试放独立文件，覆盖 handler 注册与调用路径。

- [ ] callTool outputSchema 校验测试。
  方案说明：构造带 outputSchema 的 tool，并验证 structuredContent 校验成功与失败路径。
  文档说明：说明测试验证错误类型与消息。

- [ ] request_stream/任务流测试。
  方案说明：模拟 task 流消息，确保流以 result/error 结束，且校验逻辑生效。
  文档说明：说明该测试用于保证流式协议稳定。

- [ ] capability 断言测试（请求/通知/handler）。
  方案说明：覆盖 request/notification/handler 三类断言，验证缺失 capability 的错误路径。
  文档说明：说明测试用例与 TS 行为一致。

- [ ] stdio 示例补充（基础 initialize + listTools + callTool）。
  方案说明：新增示例展示 stdio transport 的最小 client 使用流程。
  文档说明：说明示例应可配合现有 server 直接运行。

- [ ] HTTP 示例补充（streamable HTTP client + server）。
  方案说明：新增 HTTP 示例，展示初始化、请求、listChanged、任务流基础用法。
  文档说明：说明示例用于跨语言互操作验证。
