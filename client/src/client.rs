use std::fmt::Debug;

use serde_json::{Value, json};

use mcp_core::{
    protocol::{Protocol, ProtocolError},
    stdio::{JsonRpcMessage, Transport},
    types::RequestMessage,
};
use thiserror::Error;

/// Options provided when constructing a client.
#[derive(Debug, Clone)]
pub struct ClientOptions {
    /// Service name advertised by this client.
    pub service_name: String,

    /// Optional version or identifier.
    pub client_version: Option<String>,
}

impl ClientOptions {
    pub fn new(service_name: impl Into<String>) -> Self {
        Self {
            service_name: service_name.into(),
            client_version: None,
        }
    }

    pub fn with_version(mut self, version: impl Into<String>) -> Self {
        self.client_version = Some(version.into());
        self
    }
}

/// Flags describing what the client can do.
#[derive(Debug, Clone, Default)]
pub struct ClientCapabilities {
    pub supports_tools: bool,
    pub supports_prompts: bool,
    pub supports_resources: bool,
}

/// Errors that can occur while driving the client runtime.
#[derive(Debug, Error)]
pub enum ClientError<TransportError> {
    #[error("transport failed: {0}")]
    Transport(#[from] TransportError),

    #[error("protocol failed: {0}")]
    Protocol(ProtocolError),

    #[error("data serialization failed: {0}")]
    Serialization(serde_json::Error),
}

/// Minimal client that wires a `Transport` and `Protocol` together.
pub struct Client<T>
where
    T: Transport<Message = JsonRpcMessage>,
{
    #[allow(dead_code)]
    protocol: Protocol,
    transport: T,
    options: ClientOptions,
    capabilities: ClientCapabilities,
}

impl<T> Client<T>
where
    T: Transport<Message = JsonRpcMessage>,
{
    /// Create a new client instance with the provided transport and options.
    pub fn new(transport: T, options: ClientOptions) -> Self {
        Self {
            protocol: Protocol::default(),
            transport,
            options,
            capabilities: ClientCapabilities::default(),
        }
    }

    /// Configure feature flags for this client.
    pub fn with_capabilities(mut self, capabilities: ClientCapabilities) -> Self {
        self.capabilities = capabilities;
        self
    }

    /// Start the underlying transport.
    pub fn start(&mut self) -> Result<(), ClientError<T::Error>> {
        self.transport.start()?;
        Ok(())
    }

    /// Send a handshake request describing this client's metadata.
    pub fn handshake(&mut self) -> Result<(), ClientError<T::Error>> {
        let request = RequestMessage::new(
            "client-handshake",
            "client/hello",
            json!({
                "serviceName": self.options.service_name,
                "version": self.options.client_version,
                "capabilities": {
                    "tools": self.capabilities.supports_tools,
                    "prompts": self.capabilities.supports_prompts,
                    "resources": self.capabilities.supports_resources
                }
            }),
        );

        self.transport.send(&JsonRpcMessage::Request(request))?;
        Ok(())
    }

    /// Send a plain request message through the transport.
    pub fn send_request(
        &mut self,
        method: impl Into<String>,
        params: Value,
    ) -> Result<(), ClientError<T::Error>> {
        let request = RequestMessage::new("client-request", method, params);
        self.transport.send(&JsonRpcMessage::Request(request))?;
        Ok(())
    }

    /// Shutdown the transport.
    pub fn close(&mut self) -> Result<(), ClientError<T::Error>> {
        self.transport.close()?;
        Ok(())
    }
}

#[cfg(test)]
mod tests;
