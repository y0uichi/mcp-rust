"""
使用 agent-coder 创建一个完整的 Todo 应用。

运行方式：
    source .venv/bin/activate
    cd examples/todo-app
    python create_todo_app.py
"""

import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'agent-coder', 'src'))

from agent_coder import AgentCoder, AgentCoderConfig


async def create_todo_app():
    """使用 agent-coder 创建一个完整的 todo 应用。"""

    # 获取当前目录作为工作目录
    working_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"工作目录: {working_dir}")
    print("=" * 60)
    print("正在启动 agent-coder 来创建 Todo 应用...")
    print("=" * 60)

    # 配置 agent-coder
    config = AgentCoderConfig(
        model="claude-sonnet-4-20250514",
        permission_mode="bypassPermissions",  # 允许自动创建和编辑文件
        working_dir=working_dir,
        max_tokens=16000,
    )

    # 定义创建 todo 应用的提示
    prompt = """
请在当前目录下创建一个完整的 Python Todo 命令行应用。要求如下：

## 项目结构
```
todo_app/
├── __init__.py
├── models.py      # Todo 数据模型
├── manager.py     # Todo 管理器（CRUD操作）
├── storage.py     # JSON 文件持久化
└── cli.py         # 命令行接口
main.py            # 入口文件
requirements.txt   # 依赖文件
```

## 功能要求

1. **Todo 模型** (models.py):
   - id: 唯一标识符（UUID）
   - title: 标题
   - description: 描述（可选）
   - completed: 是否完成
   - priority: 优先级 (high/medium/low)
   - created_at: 创建时间
   - updated_at: 更新时间

2. **存储层** (storage.py):
   - 使用 JSON 文件存储数据
   - 支持 load 和 save 操作
   - 文件路径可配置

3. **管理器** (manager.py):
   - add(title, description, priority): 添加新待办
   - list(filter_completed): 列出待办
   - complete(id): 标记完成
   - remove(id): 删除待办
   - update(id, **kwargs): 更新待办
   - get(id): 获取单个待办

4. **CLI** (cli.py + main.py):
   使用 argparse，支持以下命令：
   - `python main.py add "买牛奶" -d "去超市" -p high`
   - `python main.py list` 或 `python main.py list --all`
   - `python main.py complete <id>`
   - `python main.py remove <id>`
   - `python main.py show <id>`

## 代码要求
- 使用类型提示
- 添加 docstring
- 错误处理
- 使用 dataclass 或 pydantic

请创建所有必要的文件。
"""

    try:
        async with AgentCoder(config=config) as agent:
            print("\n开始生成代码...\n")

            # 使用流式输出
            async for message in agent.run_stream(prompt):
                if "text" in message:
                    print(message["text"], end="", flush=True)

            print("\n\n" + "=" * 60)
            print("Todo 应用创建完成！")
            print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        raise


async def main():
    """主函数。"""
    # 检查 API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("错误: 请设置 ANTHROPIC_API_KEY 环境变量")
        print("export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)

    await create_todo_app()


if __name__ == "__main__":
    asyncio.run(main())
