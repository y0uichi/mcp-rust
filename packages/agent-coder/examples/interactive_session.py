"""
Interactive session example for agent-coder.

This example demonstrates how to use the agent for
multi-turn interactive conversations.
"""

import asyncio
from agent_coder import AgentCoder, AgentCoderConfig


async def main():
    """Run an interactive coding session."""
    # Create agent with coding assistant prompt
    config = AgentCoderConfig(
        model="claude-3-5-sonnet-20241022",
        permission_mode="acceptEdits",
        working_dir=".",
    )
    agent = AgentCoder(config=config)

    print("=== Interactive Coding Session ===")
    print("Type 'exit' or 'quit' to end the session\n")

    # Start the session with an initial message
    print("You: I'm working on a Python project. Can you help me?")
    async for msg in agent.send_message("I'm working on a Python project. Can you help me?"):
        if "text" in msg:
            print(f"Claude: {msg['text']}")

    # Interactive loop
    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print()  # Blank line before response
            async for msg in agent.send_message(user_input):
                if "text" in msg:
                    print(f"Claude: {msg['text']}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
