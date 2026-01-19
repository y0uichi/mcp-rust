//! Core runtime shared across the MCP workspace.
//! The crate mirrors the structure described in `docs/rust-rewrite-plan.md`
//! by exposing configuration helpers, transport-neutral types, schema validation,
//! and a lightweight protocol runtime.

pub mod http;
pub mod protocol;
pub mod schema;
pub mod stdio;
pub mod types;

pub use crate::protocol::{
    CancellationToken, CapabilityChecker, NotificationContext, NotificationHandler, Protocol,
    ProtocolError, ProtocolOptions, RequestContext, RequestHandler, RequestOptions, TaskStore,
};
pub use crate::schema::{JsonSchemaValidator, SchemaValidator, ValidationError};
pub use crate::stdio::{
    JsonRpcMessage, ReadBuffer, ReadBufferError, deserialize_message, serialize_message,
};
pub use crate::types::{
    CapabilityFlag, ClientCapabilities, ClientTasksCapability, ClientTasksElicitationCapabilities,
    ClientTasksRequestCapabilities, ClientTasksSamplingCapabilities,
    DEFAULT_NEGOTIATED_PROTOCOL_VERSION, ElicitationCapability, ErrorCode, ErrorObject,
    FormElicitationCapability, LATEST_PROTOCOL_VERSION, Message, MessageId, NotificationMessage,
    PromptCapabilities, RelatedTaskMetadata, RequestMessage, ResourceCapabilities, ResultMessage,
    RootsCapabilities, SUPPORTED_PROTOCOL_VERSIONS, SamplingCapabilities, ServerCapabilities,
    ServerTasksCapability, ServerTasksRequestCapabilities, ServerTasksToolCapabilities, Task,
    TaskCreationParams, TaskMetadata, TaskStatus, ToolCapabilities,
};

/// Roles that participants in the mesh can take.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Role {
    Server,
    Client,
}

/// Runtime configuration that applies to every MCP participant.
#[derive(Debug, Clone)]
pub struct CoreConfig {
    /// Human-friendly name for the service.
    pub service_name: String,
    /// TCP port that the service listens on.
    pub port: u16,
    /// Deployment environment.
    pub environment: Environment,
}

impl CoreConfig {
    /// Create a simple dev-friendly configuration.
    pub fn dev(service_name: impl Into<String>) -> Self {
        Self {
            service_name: service_name.into(),
            port: 4000,
            environment: Environment::Development,
        }
    }
}

impl Default for CoreConfig {
    fn default() -> Self {
        Self::dev("mcp-service")
    }
}

/// Environment tiers for consumers of the config.
#[derive(Debug, Clone)]
pub enum Environment {
    Development,
    Production,
}

/// Common exports to avoid repetitive imports in binaries.
pub mod prelude {
    pub use super::{
        CancellationToken, NotificationHandler, Protocol, ProtocolError, ProtocolOptions,
        RequestContext, RequestHandler, RequestOptions,
    };
    pub use super::{CoreConfig as Config, Environment};
    pub use super::{JsonSchemaValidator, SchemaValidator};
    pub use super::{Message, NotificationMessage, RequestMessage, ResultMessage, Role};
}
