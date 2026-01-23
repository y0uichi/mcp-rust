#!/usr/bin/env python3
"""
基础工作流示例。

演示如何使用 FeatureDevelopmentGraph 运行完整的功能开发流程。
"""

import os
from langgraph_1 import FeatureDevelopmentGraph


def main():
    """运行基础工作流示例。"""
    # 确保设置了 API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("请设置 ANTHROPIC_API_KEY 环境变量")
        return

    # 创建工作流
    workflow = FeatureDevelopmentGraph()

    # 定义需求
    requirement = """
    设计一个用户登录页面，要求：
    1. 支持手机号和邮箱两种登录方式
    2. 可以切换登录方式
    3. 包含记住我和忘记密码功能
    4. 登录按钮在输入有效时才可点击
    5. 显示清晰的错误提示
    """

    print("=" * 60)
    print("功能开发工作流示例")
    print("=" * 60)
    print(f"\n需求：{requirement}\n")
    print("=" * 60)

    # 运行工作流
    print("\n开始执行工作流...\n")

    result = workflow.run(
        requirement=requirement,
        max_iterations=3,
    )

    # 输出结果
    print("\n" + "=" * 60)
    print("执行结果")
    print("=" * 60)

    print("\n【交互设计】")
    print("-" * 40)
    print(result["design_spec"][:500] + "..." if len(result["design_spec"]) > 500 else result["design_spec"])

    print("\n【开发代码】")
    print("-" * 40)
    print(result["code"][:500] + "..." if len(result["code"]) > 500 else result["code"])

    print("\n【验收结果】")
    print("-" * 40)
    print(result["review_result"])

    print("\n【统计信息】")
    print("-" * 40)
    print(f"迭代次数: {result['iteration_count']}")
    print(f"验收状态: {'通过' if result['review_passed'] else '未通过'}")
    print(f"反馈记录数: {len(result['feedback'])}")


def stream_example():
    """流式输出示例。"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("请设置 ANTHROPIC_API_KEY 环境变量")
        return

    workflow = FeatureDevelopmentGraph()

    requirement = "设计一个简单的待办事项列表，支持添加和删除任务"

    print("流式执行工作流...\n")

    for event in workflow.stream(requirement=requirement, max_iterations=2):
        for node_name, output in event.items():
            print(f"\n[{node_name}] 执行完成")
            print("-" * 30)

            # 打印关键信息
            if "design_spec" in output and output["design_spec"]:
                print("产出: 交互设计文档")
            if "code" in output and output["code"]:
                print("产出: 实现代码")
            if "review_result" in output and output["review_result"]:
                passed = output.get("review_passed", False)
                print(f"产出: 验收结果 ({'通过' if passed else '不通过'})")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "stream":
        stream_example()
    else:
        main()
