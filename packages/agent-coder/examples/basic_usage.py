"""
Basic usage example for agent-coder.

This example demonstrates one-shot task execution.
"""

import asyncio
from agent_coder import AgentCoder, AgentCoderConfig


async def main():
    """Run a simple coding task."""
    # Create agent with default configuration
    agent = AgentCoder()

    # Example 1: Simple code generation
    print("=== Example 1: Code Generation ===")
    messages = await agent.run("Write a Python function to calculate fibonacci numbers")
    for msg in messages:
        if "text" in msg:
            print(msg["text"])

    # Example 2: With custom configuration
    print("\n=== Example 2: Custom Configuration ===")
    config = AgentCoderConfig(
        model="claude-3-5-sonnet-20241022",
        permission_mode="acceptEdits",
        working_dir=".",
    )
    agent_with_config = AgentCoder(config=config)

    messages = await agent_with_config.run(
        "Explain what recursion is and when to use it"
    )
    for msg in messages:
        if "text" in msg:
            print(msg["text"])

    # Example 3: Streaming response
    print("\n=== Example 3: Streaming Response ===")
    async for message in agent.run_stream("Create a class to represent a Rectangle"):
        if "text" in message:
            print(message["text"], end="", flush=True)
    print()

    # Clean up
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
