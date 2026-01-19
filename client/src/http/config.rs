//! Configuration for HTTP client transport.

use std::collections::HashMap;
use std::time::Duration;

use super::reconnect::ReconnectOptions;

/// Configuration for the HTTP client transport.
#[derive(Debug, Clone)]
pub struct HttpClientConfig {
    /// Base URL of the MCP server (e.g., "http://localhost:8080").
    pub base_url: String,

    /// Endpoint path for MCP requests (default: "/mcp").
    pub endpoint_path: String,

    /// Timeout for HTTP requests.
    pub request_timeout: Duration,

    /// Timeout for SSE connection (None for no timeout).
    pub sse_timeout: Option<Duration>,

    /// Reconnection options.
    pub reconnect_options: ReconnectOptions,

    /// Custom HTTP headers to include in requests.
    pub custom_headers: HashMap<String, String>,

    /// Whether to automatically reconnect on connection loss.
    pub auto_reconnect: bool,
}

impl HttpClientConfig {
    /// Create a new configuration with the given base URL.
    pub fn new(base_url: impl Into<String>) -> Self {
        Self {
            base_url: base_url.into(),
            endpoint_path: "/mcp".to_string(),
            request_timeout: Duration::from_secs(30),
            sse_timeout: None,
            reconnect_options: ReconnectOptions::default(),
            custom_headers: HashMap::new(),
            auto_reconnect: true,
        }
    }

    /// Set the endpoint path.
    pub fn endpoint_path(mut self, path: impl Into<String>) -> Self {
        self.endpoint_path = path.into();
        self
    }

    /// Set the request timeout.
    pub fn request_timeout(mut self, timeout: Duration) -> Self {
        self.request_timeout = timeout;
        self
    }

    /// Set the SSE timeout.
    pub fn sse_timeout(mut self, timeout: Option<Duration>) -> Self {
        self.sse_timeout = timeout;
        self
    }

    /// Set the reconnection options.
    pub fn reconnect_options(mut self, options: ReconnectOptions) -> Self {
        self.reconnect_options = options;
        self
    }

    /// Add a custom header.
    pub fn header(mut self, name: impl Into<String>, value: impl Into<String>) -> Self {
        self.custom_headers.insert(name.into(), value.into());
        self
    }

    /// Set whether to automatically reconnect.
    pub fn auto_reconnect(mut self, enabled: bool) -> Self {
        self.auto_reconnect = enabled;
        self
    }

    /// Get the full endpoint URL.
    pub fn endpoint_url(&self) -> String {
        let base = self.base_url.trim_end_matches('/');
        let path = if self.endpoint_path.starts_with('/') {
            self.endpoint_path.clone()
        } else {
            format!("/{}", self.endpoint_path)
        };
        format!("{}{}", base, path)
    }
}

impl Default for HttpClientConfig {
    fn default() -> Self {
        Self::new("http://localhost:8080")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_endpoint_url() {
        let config = HttpClientConfig::new("http://localhost:8080");
        assert_eq!(config.endpoint_url(), "http://localhost:8080/mcp");

        let config = HttpClientConfig::new("http://localhost:8080/");
        assert_eq!(config.endpoint_url(), "http://localhost:8080/mcp");

        let config = HttpClientConfig::new("http://localhost:8080").endpoint_path("api/mcp");
        assert_eq!(config.endpoint_url(), "http://localhost:8080/api/mcp");
    }
}
