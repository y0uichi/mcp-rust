use async_trait::async_trait;
use serde_json::Value;
use std::{collections::HashMap, sync::Arc};

use crate::schema::{SchemaValidator, ValidationError};
use crate::types::{RequestMessage, ResultMessage};
use thiserror::Error;

/// Handler that processes a single JSON-RPC-style request.
#[async_trait]
pub trait RequestHandler: Send + Sync + 'static {
    async fn handle(&self, request: &RequestMessage) -> Result<Value, ProtocolError>;
}

struct HandlerRegistration<S> {
    handler: Arc<dyn RequestHandler>,
    schema: S,
}

/// A tiny JSON-RPC protocol runtime inspired by the MCP core plan.
pub struct Protocol<V: SchemaValidator = crate::schema::JsonSchemaValidator> {
    validator: V,
    handlers: HashMap<String, HandlerRegistration<V::Schema>>,
}

impl<V: SchemaValidator> Protocol<V> {
    /// Create a new protocol runtime that validates incoming payloads.
    pub fn new(validator: V) -> Self {
        Self {
            validator,
            handlers: HashMap::new(),
        }
    }

    /// Register a handler together with the schema that describes its params.
    pub fn register_handler<H>(&mut self, method: impl Into<String>, schema: V::Schema, handler: H)
    where
        H: RequestHandler,
    {
        self.handlers.insert(
            method.into(),
            HandlerRegistration {
                handler: Arc::new(handler),
                schema,
            },
        );
    }

    /// Handle a request by validating it and invoking the handler.
    pub async fn handle_request(
        &self,
        request: RequestMessage,
    ) -> Result<ResultMessage, ProtocolError> {
        let entry = self
            .handlers
            .get(&request.method)
            .ok_or_else(|| ProtocolError::UnknownMethod(request.method.clone()))?;

        self.validator.validate(&entry.schema, &request.params)?;

        let result_value = entry.handler.handle(&request).await?;
        Ok(ResultMessage::success(request.id.clone(), result_value))
    }
}

impl Default for Protocol<crate::schema::JsonSchemaValidator> {
    fn default() -> Self {
        Self::new(crate::schema::JsonSchemaValidator::default())
    }
}

/// Errors that can occur inside the protocol runtime.
#[derive(Debug, Error)]
pub enum ProtocolError {
    #[error("no handler registered for method `{0}`")]
    UnknownMethod(String),

    #[error(transparent)]
    Validation(#[from] ValidationError),

    #[error("handler failed: {0}")]
    Handler(String),

    #[error("serialization failed: {0}")]
    Serialization(#[from] serde_json::Error),
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::schema::JsonSchemaValidator;
    use crate::types::RequestMessage;
    use futures::executor::block_on;
    use schemars::JsonSchema;
    use serde::{Deserialize, Serialize};
    use serde_json::json;

    #[derive(Debug, Deserialize, Serialize, JsonSchema)]
    struct EchoParams {
        text: String,
    }

    struct EchoHandler;

    #[async_trait]
    impl RequestHandler for EchoHandler {
        async fn handle(&self, request: &RequestMessage) -> Result<Value, ProtocolError> {
            let params: EchoParams = serde_json::from_value(request.params.clone())?;
            Ok(json!({ "echo": params.text }))
        }
    }

    #[test]
    fn handles_valid_request() {
        let mut protocol = Protocol::new(JsonSchemaValidator::default());
        protocol.register_handler(
            "echo",
            JsonSchemaValidator::schema_for::<EchoParams>(),
            EchoHandler,
        );

        let request = RequestMessage::new("1", "echo", json!({ "text": "hello" }));
        let response = block_on(protocol.handle_request(request)).expect("valid response");
        assert!(response.error.is_none());
        assert_eq!(response.result.unwrap()["echo"], "hello");
    }

    #[test]
    fn rejects_unknown_method() {
        let protocol = Protocol::new(JsonSchemaValidator::default());
        let request = RequestMessage::new("1", "missing", json!({}));
        let err = block_on(protocol.handle_request(request)).expect_err("should error");
        assert!(matches!(err, ProtocolError::UnknownMethod(method) if method == "missing"));
    }
}
