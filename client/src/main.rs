use std::{env, thread::sleep, time::Duration};

use mcp_client::stdio::{
    JsonRpcMessage, StdioClientTransport, StdioClientTransportError, StdioServerParameters,
    StdioStream, Transport,
};
use mcp_core::{CoreConfig, Message, RequestMessage, Role};
use serde_json::json;

fn main() {
    if let Err(error) = run() {
        eprintln!("Client error: {error}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), StdioClientTransportError> {
    let config = CoreConfig::dev("mcp-client");
    announce_role(Role::Client, &config);

    let (command, args) = resolve_server_command();
    let mut transport = StdioClientTransport::new(
        StdioServerParameters::new(command)
            .args(args)
            .stderr(StdioStream::Inherit),
    );

    transport
        .on_message(|message| println!("stdio message: {:?}", message))
        .on_error(|error| eprintln!("stdio transport error: {error}"))
        .on_close(|| println!("stdio transport closed"));

    let transport_iface: &mut dyn Transport<Message = JsonRpcMessage, Error = StdioClientTransportError> =
        &mut transport;

    transport_iface.start()?;

    let handshake = create_request(&config);
    println!("Sending: {}", handshake.summary());

    let request = JsonRpcMessage::Request(RequestMessage::new(
        "client-handshake",
        "mcp-server",
        json!({
            "sender": handshake.sender,
            "recipient": handshake.recipient,
            "body": handshake.body
        }),
    ));

    transport_iface.send(&request)?;

    println!(
        "Client expects handshake on port {} and will reuse {:?}.",
        config.port, config.environment
    );

    sleep(Duration::from_secs(1));
    transport_iface.close()?;
    Ok(())
}

fn announce_role(role: Role, config: &CoreConfig) {
    println!(
        "Running {} in {:?} mode (role: {:?})",
        config.service_name, config.environment, role
    );
}

fn create_request(config: &CoreConfig) -> Message {
    Message::new(
        &config.service_name,
        "mcp-server",
        "greetings from the client mesh peer",
    )
}

#[cfg(target_os = "windows")]
const DEFAULT_SERVER_COMMAND: &str = "powershell";

#[cfg(not(target_os = "windows"))]
const DEFAULT_SERVER_COMMAND: &str = "cat";

#[cfg(target_os = "windows")]
const DEFAULT_SERVER_ARGS: &[&str] = &["-NoLogo", "-Command", "Get-Content -Raw -"];

#[cfg(not(target_os = "windows"))]
const DEFAULT_SERVER_ARGS: &[&str] = &[];

fn resolve_server_command() -> (String, Vec<String>) {
    if let Ok(command) = env::var("MCP_CLIENT_STDIO_COMMAND") {
        let args = env::var("MCP_CLIENT_STDIO_ARGS")
            .map(|value| value.split_whitespace().map(String::from).collect())
            .unwrap_or_default();
        return (command, args);
    }

    let mut args_iter = env::args().skip(1);
    let command = args_iter
        .next()
        .unwrap_or_else(|| DEFAULT_SERVER_COMMAND.to_string());
    let rest: Vec<String> = args_iter.collect();

    if rest.is_empty() {
        (
            command,
            DEFAULT_SERVER_ARGS
                .iter()
                .map(|arg| arg.to_string())
                .collect(),
        )
    } else {
        (command, rest)
    }
}
