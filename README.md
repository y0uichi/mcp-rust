# MCP Workspace

This workspace illustrates how to split a small Rust system into a shared core with dedicated server and client binaries.

## Structure
- `core` (`mcp_core`): a library that owns configuration, message helpers, shared enums, JSON-RPC request/notification/result types, schema validation, and a lightweight `Protocol` runtime inspired by the Rust rewrite plan.
- `server` (`mcp_server`): a binary that depends on `mcp_core` to announce itself as a server and reply to incoming messages.
- `client` (`mcp_client`): a binary that depends on `mcp_core` to build requests and display the client's operational stance.

Each crate lives in a top-level directory with the same name, and the workspace manifest exposes them via `members`.

## Recommendations
1. Start by editing `core` to add domain-specific structures and validation logic.
2. Keep `server` and `client` focused on wiring and logging, pulling shared routines through `mcp_core`.
3. Use `cargo run -p mcp_server` and `cargo run -p mcp_client` to exercise each binary; `cargo test` all members via `cargo test`.
4. Future work could introduce feature flags on `mcp_core`, integration tests that exercise both binaries, or a `mcp-cli` helper to orchestrate both sides.

## How to Get Going
```sh
cargo build           # builds all members
cargo run -p mcp_server
cargo run -p mcp_client
```

This layout keeps shared logic centralized while letting each binary evolve independently.
