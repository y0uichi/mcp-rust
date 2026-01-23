#!/usr/bin/env python3
"""Todo 应用入口。

使用示例:
    # 添加待办
    python main.py add "买牛奶" -d "去超市买" -p high

    # 列出待办
    python main.py list
    python main.py list --all

    # 标记完成
    python main.py complete <id>

    # 删除待办
    python main.py remove <id>

    # 查看详情
    python main.py show <id>

    # 统计信息
    python main.py stats

    # 清除已完成
    python main.py clear
"""

import sys
from todo_app.cli import run_cli


if __name__ == "__main__":
    sys.exit(run_cli())
