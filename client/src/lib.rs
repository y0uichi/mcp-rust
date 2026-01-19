//! Streamline stdio helpers for the client binary.
pub mod client;
pub mod http;
pub mod stdio;
pub mod websocket;

pub use stdio::{
    DEFAULT_INHERITED_ENV_VARS, JsonRpcMessage, ReadBuffer, StdioClientTransport,
    StdioClientTransportError, StdioServerParameters, StdioStream, Transport, deserialize_message,
    get_default_environment, serialize_message,
};

pub use client::{Client, ClientCapabilities, ClientError, ClientOptions};

pub use http::{
    HttpClientConfig, HttpClientError, HttpClientTransport, LegacySseClientConfig,
    LegacySseClientTransport, ReconnectOptions,
};

#[cfg(feature = "websocket")]
pub use websocket::{WebSocketClientError, WebSocketClientTransport};
