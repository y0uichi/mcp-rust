//! Example: MCP HTTP Server with Streamable HTTP Transport
//!
//! This example demonstrates how to run an MCP server over HTTP with SSE support.
//! It uses `tiny_http` as a simple HTTP server framework.
//!
//! Endpoints:
//! - POST /mcp - Send JSON-RPC messages
//! - GET /mcp - Establish SSE connection for receiving messages
//! - DELETE /mcp - Close session
//!
//! Run with: cargo run -p mcp-http-server
//! Test with: curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" \
//!            -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"0.1.0"}}}'

use std::io::Read;
use std::sync::Arc;
use std::thread;

use mcp_core::protocol::RequestContext;
use mcp_core::types::{
    BaseMetadata, CallToolResult, ContentBlock, Icons, Implementation, ServerCapabilities,
    TextContent, Tool,
};
use mcp_server::{
    HttpResponse, HttpServerHandler, HttpServerOptions, McpServer, ServerError, ServerOptions,
    SessionConfig,
};
use serde_json::json;

fn main() {
    if let Err(e) = run() {
        eprintln!("Server error: {}", e);
        std::process::exit(1);
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    // Create server info
    let server_info = Implementation {
        base: BaseMetadata {
            name: "mcp-http-server-example".to_string(),
            title: Some("MCP HTTP Server Example".to_string()),
        },
        icons: Icons::default(),
        version: "0.1.0".to_string(),
        website_url: None,
        description: Some("Example MCP server with HTTP/SSE transport".to_string()),
    };

    // Configure server capabilities
    let mut server_options = ServerOptions::default();
    server_options.capabilities = Some(ServerCapabilities {
        tools: Some(mcp_core::types::ToolCapabilities {
            list_changed: Some(true),
        }),
        ..Default::default()
    });
    server_options.instructions = Some("This is an example HTTP MCP server.".to_string());

    // Create MCP server
    let mut mcp_server = McpServer::new(server_info, server_options);

    // Register example tools
    register_tools(&mut mcp_server)?;

    // Create HTTP handler
    let http_options = HttpServerOptions {
        session_config: SessionConfig {
            max_sessions: 100,
            session_timeout: std::time::Duration::from_secs(30 * 60),
            cleanup_interval: std::time::Duration::from_secs(60),
        },
        enable_sse: true,
        enable_single_response: true,
        base_url: Some("http://localhost:8080".to_string()),
        endpoint_path: "/mcp".to_string(),
    };
    let handler = Arc::new(HttpServerHandler::new(Arc::new(mcp_server), http_options));

    // Start cleanup thread
    let cleanup_handler = Arc::clone(&handler);
    thread::spawn(move || loop {
        thread::sleep(std::time::Duration::from_secs(60));
        let cleaned = cleanup_handler.cleanup_sessions();
        if cleaned > 0 {
            eprintln!("Cleaned up {} expired sessions", cleaned);
        }
    });

    // Start HTTP server
    let addr = "0.0.0.0:8080";
    let server = tiny_http::Server::http(addr).map_err(|e| format!("Failed to bind: {}", e))?;

    println!("MCP HTTP Server listening on http://{}", addr);
    println!();
    println!("Endpoints:");
    println!("  POST   http://{}/mcp - Send JSON-RPC messages", addr);
    println!("  GET    http://{}/mcp - Establish SSE connection", addr);
    println!("  DELETE http://{}/mcp - Close session", addr);
    println!();
    println!("Example request:");
    println!(r#"  curl -X POST http://localhost:8080/mcp \"#);
    println!(r#"       -H "Content-Type: application/json" \"#);
    println!(r#"       -d '{{"jsonrpc":"2.0","id":1,"method":"initialize","params":{{"protocolVersion":"2025-03-26","capabilities":{{}},"clientInfo":{{"name":"test","version":"0.1.0"}}}}}}'"#);
    println!();

    // Handle requests
    for request in server.incoming_requests() {
        let handler = Arc::clone(&handler);
        thread::spawn(move || {
            if let Err(e) = handle_request(request, &handler) {
                eprintln!("Request error: {}", e);
            }
        });
    }

    Ok(())
}

fn handle_request(
    mut request: tiny_http::Request,
    handler: &HttpServerHandler,
) -> Result<(), Box<dyn std::error::Error>> {
    let path = request.url().to_string();
    let method = request.method().to_string();

    // Only handle /mcp endpoint
    if !path.starts_with("/mcp") {
        let response = tiny_http::Response::from_string("Not Found")
            .with_status_code(404);
        request.respond(response)?;
        return Ok(());
    }

    // Extract headers (convert to String for case-insensitive comparison)
    let session_id = request
        .headers()
        .iter()
        .find(|h| h.field.to_string().to_lowercase() == "mcp-session-id")
        .map(|h| h.value.to_string());

    let content_type = request
        .headers()
        .iter()
        .find(|h| h.field.to_string().to_lowercase() == "content-type")
        .map(|h| h.value.to_string());

    let accept = request
        .headers()
        .iter()
        .find(|h| h.field.to_string().to_lowercase() == "accept")
        .map(|h| h.value.to_string());

    let last_event_id = request
        .headers()
        .iter()
        .find(|h| h.field.to_string().to_lowercase() == "last-event-id")
        .map(|h| h.value.to_string());

    // Log request
    eprintln!(
        "[{}] {} {} (session: {:?})",
        chrono_simple(),
        method,
        path,
        session_id
    );

    // Handle based on method
    let http_response = match method.as_str() {
        "POST" => {
            // Read body
            let mut body = Vec::new();
            request.as_reader().read_to_end(&mut body)?;
            handler.handle_post(
                session_id.as_deref(),
                content_type.as_deref(),
                &body,
            )
        }
        "GET" => handler.handle_get(
            session_id.as_deref(),
            last_event_id.as_deref(),
            accept.as_deref(),
        ),
        "DELETE" => handler.handle_delete(session_id.as_deref()),
        _ => HttpResponse::Error {
            status: 405,
            message: "Method not allowed".to_string(),
        },
    };

    // Send response
    match http_response {
        HttpResponse::Json {
            status,
            body,
            session_id: new_session_id,
        } => {
            let mut response = tiny_http::Response::from_string(body)
                .with_status_code(status)
                .with_header(
                    tiny_http::Header::from_bytes(&b"Content-Type"[..], &b"application/json"[..])
                        .unwrap(),
                );

            if let Some(sid) = new_session_id {
                response = response.with_header(
                    tiny_http::Header::from_bytes(&b"Mcp-Session-Id"[..], sid.as_bytes()).unwrap(),
                );
            }

            request.respond(response)?;
        }
        HttpResponse::Sse {
            session_id: sid,
            writer_fn,
        } => {
            // For SSE, we need to send headers and keep connection open
            // Note: tiny_http doesn't support true streaming well, so this is simplified
            let headers = vec![
                tiny_http::Header::from_bytes(&b"Content-Type"[..], &b"text/event-stream"[..])
                    .unwrap(),
                tiny_http::Header::from_bytes(&b"Cache-Control"[..], &b"no-cache"[..]).unwrap(),
                tiny_http::Header::from_bytes(&b"Connection"[..], &b"keep-alive"[..]).unwrap(),
                tiny_http::Header::from_bytes(&b"Mcp-Session-Id"[..], sid.as_bytes()).unwrap(),
            ];

            // Create a simple SSE response
            let mut sse_body = String::new();
            sse_body.push_str(&format!("event: session\ndata: {}\n\n", sid));
            sse_body.push_str(":ping\n\n");

            let response = tiny_http::Response::from_string(sse_body)
                .with_status_code(200)
                .with_header(headers[0].clone())
                .with_header(headers[1].clone())
                .with_header(headers[2].clone())
                .with_header(headers[3].clone());

            request.respond(response)?;
        }
        HttpResponse::Empty { status } => {
            let response = tiny_http::Response::empty(status);
            request.respond(response)?;
        }
        HttpResponse::Error { status, message } => {
            let error_body = serde_json::json!({
                "jsonrpc": "2.0",
                "id": null,
                "error": {
                    "code": -32000,
                    "message": message
                }
            });

            let response = tiny_http::Response::from_string(error_body.to_string())
                .with_status_code(status)
                .with_header(
                    tiny_http::Header::from_bytes(&b"Content-Type"[..], &b"application/json"[..])
                        .unwrap(),
                );

            request.respond(response)?;
        }
    }

    Ok(())
}

fn register_tools(server: &mut McpServer) -> Result<(), Box<dyn std::error::Error>> {
    // Register an echo tool
    server.register_tool(
        Tool {
            base: BaseMetadata {
                name: "echo".to_string(),
                title: Some("Echo Tool".to_string()),
            },
            icons: Icons::default(),
            description: Some("Echoes back the input message".to_string()),
            input_schema: json!({
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to echo"
                    }
                },
                "required": ["message"]
            }),
            output_schema: None,
            annotations: None,
            execution: None,
            meta: None,
        },
        |params: Option<serde_json::Value>, _context: RequestContext| {
            Box::pin(async move {
                let message = params
                    .as_ref()
                    .and_then(|p| p.get("message"))
                    .and_then(|v| v.as_str())
                    .unwrap_or("(no message)");

                Ok::<_, ServerError>(CallToolResult {
                    content: vec![ContentBlock::Text(TextContent::new(format!(
                        "Echo: {}",
                        message
                    )))],
                    structured_content: None,
                    is_error: None,
                    meta: None,
                })
            })
        },
    )?;

    // Register a greeting tool
    server.register_tool(
        Tool {
            base: BaseMetadata {
                name: "greet".to_string(),
                title: Some("Greeting Tool".to_string()),
            },
            icons: Icons::default(),
            description: Some("Generates a greeting message".to_string()),
            input_schema: json!({
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet"
                    }
                },
                "required": ["name"]
            }),
            output_schema: None,
            annotations: None,
            execution: None,
            meta: None,
        },
        |params: Option<serde_json::Value>, _context: RequestContext| {
            Box::pin(async move {
                let name = params
                    .as_ref()
                    .and_then(|p| p.get("name"))
                    .and_then(|v| v.as_str())
                    .unwrap_or("World");

                Ok::<_, ServerError>(CallToolResult {
                    content: vec![ContentBlock::Text(TextContent::new(format!(
                        "Hello, {}! Welcome to MCP over HTTP.",
                        name
                    )))],
                    structured_content: None,
                    is_error: None,
                    meta: None,
                })
            })
        },
    )?;

    // Register a time tool
    server.register_tool(
        Tool {
            base: BaseMetadata {
                name: "current_time".to_string(),
                title: Some("Current Time".to_string()),
            },
            icons: Icons::default(),
            description: Some("Returns the current server time".to_string()),
            input_schema: json!({
                "type": "object",
                "properties": {}
            }),
            output_schema: None,
            annotations: None,
            execution: None,
            meta: None,
        },
        |_params: Option<serde_json::Value>, _context: RequestContext| {
            Box::pin(async move {
                let now = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs();

                Ok::<_, ServerError>(CallToolResult {
                    content: vec![ContentBlock::Text(TextContent::new(format!(
                        "Current Unix timestamp: {}",
                        now
                    )))],
                    structured_content: None,
                    is_error: None,
                    meta: None,
                })
            })
        },
    )?;

    Ok(())
}

fn chrono_simple() -> String {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    format!("{}", now)
}
