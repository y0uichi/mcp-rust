use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use serde_json::Value;

/// Unique identifier used for requests and responses.
pub type MessageId = String;

/// JSON-RPC 2.0 style request payload.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, PartialEq)]
pub struct RequestMessage {
    pub jsonrpc: String,
    pub id: MessageId,
    pub method: String,
    pub params: Value,
}

impl RequestMessage {
    /// Creates a new request with the provided `id`.
    pub fn new(id: impl Into<MessageId>, method: impl Into<String>, params: Value) -> Self {
        Self {
            jsonrpc: "2.0".to_owned(),
            id: id.into(),
            method: method.into(),
            params,
        }
    }
}

/// Notification follows the same shape as a request but omits `id`.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, PartialEq)]
pub struct NotificationMessage {
    pub jsonrpc: String,
    pub method: String,
    pub params: Option<Value>,
}

impl NotificationMessage {
    pub fn new(method: impl Into<String>, params: Option<Value>) -> Self {
        Self {
            jsonrpc: "2.0".to_owned(),
            method: method.into(),
            params,
        }
    }
}

/// Response payload emitted by `Protocol`.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, PartialEq)]
pub struct ResultMessage {
    pub jsonrpc: String,
    pub id: MessageId,
    pub result: Option<Value>,
    pub error: Option<ErrorObject>,
}

impl ResultMessage {
    pub fn success(id: impl Into<MessageId>, result: Value) -> Self {
        Self {
            jsonrpc: "2.0".to_owned(),
            id: id.into(),
            result: Some(result),
            error: None,
        }
    }

    pub fn failure(id: impl Into<MessageId>, error: ErrorObject) -> Self {
        Self {
            jsonrpc: "2.0".to_owned(),
            id: id.into(),
            result: None,
            error: Some(error),
        }
    }
}

/// Standardized error object that mirrors JSON-RPC's error shape.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, PartialEq)]
pub struct ErrorObject {
    pub code: i32,
    pub message: String,
    pub data: Option<Value>,
}

impl ErrorObject {
    pub fn new(code: i32, message: impl Into<String>, data: Option<Value>) -> Self {
        Self {
            code,
            message: message.into(),
            data,
        }
    }
}

/// General-purpose message used for example logging between runtimes.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, PartialEq)]
pub struct Message {
    pub sender: String,
    pub recipient: String,
    pub body: String,
}

impl Message {
    /// Creates a new transport-agnostic message.
    pub fn new(
        sender: impl Into<String>,
        recipient: impl Into<String>,
        body: impl Into<String>,
    ) -> Self {
        Self {
            sender: sender.into(),
            recipient: recipient.into(),
            body: body.into(),
        }
    }

    /// Creates a short summary for CLI logging.
    pub fn summary(&self) -> String {
        format!("[{} -> {}] {}", self.sender, self.recipient, self.body)
    }
}
