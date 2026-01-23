"""命令行接口。"""

import argparse
import sys
from typing import Optional

from .manager import TodoManager
from .models import Priority


def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="todo",
        description="简单的命令行待办事项管理工具",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # add 命令
    add_parser = subparsers.add_parser("add", help="添加新待办")
    add_parser.add_argument("title", help="待办标题")
    add_parser.add_argument("-d", "--description", help="待办描述")
    add_parser.add_argument(
        "-p", "--priority",
        choices=["high", "medium", "low"],
        default="medium",
        help="优先级 (默认: medium)"
    )

    # list 命令
    list_parser = subparsers.add_parser("list", aliases=["ls"], help="列出待办")
    list_parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="显示所有待办（包括已完成）"
    )

    # complete 命令
    complete_parser = subparsers.add_parser("complete", aliases=["done"], help="标记完成")
    complete_parser.add_argument("id", help="待办 ID")

    # remove 命令
    remove_parser = subparsers.add_parser("remove", aliases=["rm"], help="删除待办")
    remove_parser.add_argument("id", help="待办 ID")

    # show 命令
    show_parser = subparsers.add_parser("show", help="查看待办详情")
    show_parser.add_argument("id", help="待办 ID")

    # stats 命令
    subparsers.add_parser("stats", help="显示统计信息")

    # clear 命令
    subparsers.add_parser("clear", help="清除已完成的待办")

    return parser


def print_todo_detail(todo) -> None:
    """打印待办详情。"""
    status = "已完成 ✓" if todo.completed else "进行中 ○"
    priority_text = {
        Priority.HIGH: "高 🔴",
        Priority.MEDIUM: "中 🟡",
        Priority.LOW: "低 🟢",
    }

    print(f"\n{'─' * 40}")
    print(f"ID:       {todo.id}")
    print(f"标题:     {todo.title}")
    if todo.description:
        print(f"描述:     {todo.description}")
    print(f"状态:     {status}")
    print(f"优先级:   {priority_text.get(todo.priority, todo.priority.value)}")
    print(f"创建时间: {todo.created_at}")
    print(f"更新时间: {todo.updated_at}")
    print(f"{'─' * 40}\n")


def run_cli(args: Optional[list] = None) -> int:
    """运行 CLI。

    Args:
        args: 命令行参数（用于测试）

    Returns:
        退出码
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 0

    manager = TodoManager()

    if parsed.command == "add":
        todo = manager.add(
            title=parsed.title,
            description=parsed.description,
            priority=parsed.priority,
        )
        print(f"✓ 已添加: {todo}")

    elif parsed.command in ("list", "ls"):
        todos = manager.list(show_completed=parsed.all)
        if not todos:
            print("没有待办事项。")
        else:
            print(f"\n{'待办列表':^40}")
            print("─" * 40)
            for todo in todos:
                print(f"  {todo}")
            print("─" * 40)
            stats = manager.stats
            print(f"  共 {stats['total']} 项，已完成 {stats['completed']} 项\n")

    elif parsed.command in ("complete", "done"):
        todo = manager.complete(parsed.id)
        if todo:
            print(f"✓ 已完成: {todo}")
        else:
            print(f"✗ 未找到 ID 为 '{parsed.id}' 的待办")
            return 1

    elif parsed.command in ("remove", "rm"):
        if manager.remove(parsed.id):
            print(f"✓ 已删除 ID: {parsed.id}")
        else:
            print(f"✗ 未找到 ID 为 '{parsed.id}' 的待办")
            return 1

    elif parsed.command == "show":
        todo = manager.get(parsed.id)
        if todo:
            print_todo_detail(todo)
        else:
            print(f"✗ 未找到 ID 为 '{parsed.id}' 的待办")
            return 1

    elif parsed.command == "stats":
        stats = manager.stats
        print(f"\n📊 统计信息")
        print(f"─" * 20)
        print(f"  总计:   {stats['total']}")
        print(f"  待完成: {stats['pending']}")
        print(f"  已完成: {stats['completed']}")
        print()

    elif parsed.command == "clear":
        count = manager.clear_completed()
        print(f"✓ 已清除 {count} 个已完成的待办")

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
