//! HTTP transport module for MCP server.
//!
//! This module provides HTTP-based transport for the MCP server, supporting:
//! - POST requests for sending JSON-RPC messages
//! - GET requests for establishing SSE connections
//! - DELETE requests for closing sessions

mod error;
mod handler;
mod session_manager;
mod sse_writer;

pub use error::HttpServerError;
pub use handler::{HttpResponse, HttpServerHandler, HttpServerOptions, RequestHeaders};
pub use session_manager::{SessionConfig, SessionManager, SessionState};
pub use sse_writer::{SseResponseBuilder, SseWriter};
