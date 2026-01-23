"""
Command-line interface for agent-coder.

Provides both interactive mode and single-shot task execution.
"""

import asyncio
import gc
import sys
from typing import NoReturn

import click
from claude_agent_sdk._errors import CLIConnectionError

from . import AgentCoder, AgentCoderConfig, __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.option(
    "--model",
    default="claude-3-5-sonnet-20241022",
    help="Claude model to use",
    show_default=True,
)
@click.option(
    "--working-dir", "-C",
    default=".",
    help="Working directory for file operations",
    show_default=True,
)
@click.option(
    "--permission-mode",
    default="acceptEdits",
    type=click.Choice(["default", "acceptEdits", "plan", "bypassPermissions"]),
    help="Permission mode for tool usage",
    show_default=True,
)
@click.pass_context
def cli(ctx, model, working_dir, permission_mode) -> None:
    """
    agent-coder - AI-powered coding assistant.

    Without arguments, starts an interactive session.

    Use 'ac run "your prompt"' for single-shot execution.
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = AgentCoderConfig(
        model=model,
        working_dir=working_dir,
        permission_mode=permission_mode,
    )

    # If no subcommand, start interactive mode
    if ctx.invoked_subcommand is None:
        ctx.invoke(interactive)


@cli.command()
@click.argument("prompt", required=False)
@click.option(
    "--stream", "-s",
    is_flag=True,
    help="Stream responses in real-time",
)
@click.pass_context
def run(ctx, prompt, stream) -> None:
    """
    Execute a coding task and print the result.

    If no prompt is provided, reads from stdin.
    """
    config = ctx.obj["config"]

    if not prompt:
        # Read from stdin if no prompt provided
        prompt = sys.stdin.read()

    if not prompt.strip():
        click.echo("Error: No prompt provided", err=True)
        raise SystemExit(1)

    async def _run() -> None:
        agent = AgentCoder(config=config)

        try:
            if stream:
                async for message in agent.run_stream(prompt):
                    _print_message(message)
            else:
                messages = await agent.run(prompt)
                for message in messages:
                    _print_message(message)
        except ExceptionGroup as eg:
            # 过滤掉关闭期间的 CLIConnectionError (SDK 竞态条件 bug)
            non_connection_errors = [
                e for e in eg.exceptions
                if not isinstance(e, CLIConnectionError)
            ]
            if non_connection_errors:
                raise ExceptionGroup("errors", non_connection_errors)
            # 仅有 CLIConnectionError 表示关闭时的竞态条件，可以忽略
        finally:
            await agent.close()

    # 使用自定义事件循环来正确清理子进程
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_run())
    finally:
        # 清理待处理的任务和子进程
        try:
            # 取消所有待处理任务
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            # 关闭异步生成器
            loop.run_until_complete(loop.shutdown_asyncgens())
            # 关闭默认执行器
            loop.run_until_complete(loop.shutdown_default_executor())
        finally:
            loop.close()
        # 强制垃圾回收以在事件循环关闭前清理子进程
        gc.collect()


@cli.command()
@click.option(
    "--prompt", "-p",
    help="Initial message to start the session",
)
@click.pass_context
def interactive(ctx, prompt) -> None:
    """
    Start an interactive coding session.

    Type your messages and get AI assistance.
    Use 'exit' or 'quit' to end the session.
    """
    config = ctx.obj["config"]

    async def _interactive() -> NoReturn:
        agent = AgentCoder(config=config)

        # Print welcome message
        click.echo(f"\n  agent-coder v{__version__}")
        click.echo(f"  Model: {config.model}")
        click.echo(f"  Working directory: {config.working_dir.absolute()}")
        click.echo("\n  Type 'exit' or 'quit' to end the session\n")

        try:
            # Send initial prompt if provided
            if prompt:
                click.echo(f"You: {prompt}")
                click.echo()
                async for msg in agent.send_message(prompt):
                    _print_message(msg)

            # Main interaction loop
            while True:
                try:
                    user_input = input("\033[92mYou:\033[0m ").strip()

                    if user_input.lower() in {"exit", "quit", ":q"}:
                        click.echo("\nGoodbye!")
                        break

                    if not user_input:
                        continue

                    click.echo()
                    async for msg in agent.send_message(user_input):
                        _print_message(msg)

                except EOFError:
                    click.echo("\nGoodbye!")
                    break
                except KeyboardInterrupt:
                    click.echo("\nUse 'exit' to quit, or Ctrl+D to force exit.")
        finally:
            await agent.close()
        raise SystemExit(0)

    try:
        asyncio.run(_interactive())
    except SystemExit:
        pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def analyze(ctx, file_path) -> None:
    """Analyze a code file and show insights."""
    config = ctx.obj["config"]

    async def _analyze() -> None:
        agent = AgentCoder(config=config)
        prompt = f"Analyze this file: {file_path}. Explain its structure, patterns, and any potential improvements."
        messages = await agent.run(prompt)
        for message in messages:
            _print_message(message)
        await agent.close()

    asyncio.run(_analyze())


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def explain(ctx, file_path) -> None:
    """Explain what a code file does."""
    config = ctx.obj["config"]

    async def _explain() -> None:
        agent = AgentCoder(config=config)
        prompt = f"Explain this code file: {file_path}. What does it do?"
        messages = await agent.run(prompt)
        for message in messages:
            _print_message(message)
        await agent.close()

    asyncio.run(_explain())


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def test(ctx, file_path) -> None:
    """Generate unit tests for a code file."""
    config = ctx.obj["config"]

    async def _test() -> None:
        agent = AgentCoder(config=config)
        prompt = f"Generate comprehensive unit tests for: {file_path}"
        messages = await agent.run(prompt)
        for message in messages:
            _print_message(message)
        await agent.close()

    asyncio.run(_test())


def _print_message(message: dict) -> None:
    """Print a message to stdout."""
    if "text" in message:
        click.echo(message["text"], nl=False)
    elif "tool_use" in message:
        tool_name = message["tool_use"].get("name", "unknown")
        click.echo(f"\033[90m[using {tool_name}]\033[0m", nl=True)
    elif "tool_result" in message:
        result = message["tool_result"]
        if result.get("is_error"):
            click.echo(f"\033[91m[error]\033[0m {result.get('content', [{}])[0].get('text', '')}", nl=True)


def main() -> None:
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
