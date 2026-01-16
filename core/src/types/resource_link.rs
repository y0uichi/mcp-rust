use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::Resource;

/// Resource link content block.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, PartialEq)]
pub struct ResourceLink {
    #[serde(rename = "type")]
    pub kind: String,
    #[serde(flatten)]
    pub resource: Resource,
}

impl ResourceLink {
    pub fn new(resource: Resource) -> Self {
        Self {
            kind: "resource_link".to_string(),
            resource,
        }
    }
}
