//! Streamline stdio helpers for the client binary.
pub mod stdio;

pub use stdio::{
    DEFAULT_INHERITED_ENV_VARS, JsonRpcMessage, ReadBuffer, StdioClientTransport,
    StdioClientTransportError, StdioServerParameters, StdioStream, Transport, deserialize_message,
    get_default_environment, serialize_message,
};
