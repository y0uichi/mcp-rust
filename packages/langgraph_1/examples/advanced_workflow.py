#!/usr/bin/env python3
"""
高级工作流示例。

演示更多 LangGraph 特性：
1. 使用 Checkpointer 保存状态
2. 人工介入（Human-in-the-loop）
3. 并行执行
4. 子图嵌套
"""

import os
from typing import TypedDict, Literal, Annotated
from operator import add

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage


# =============================================================================
# 扩展状态：支持更多角色
# =============================================================================

class ExtendedFeatureState(TypedDict):
    """扩展的功能开发状态，支持更多角色。"""

    # 需求
    requirement: str

    # 产品经理输出
    prd: str  # 产品需求文档

    # 交互设计师输出
    design_spec: str

    # 开发输出（分前后端）
    frontend_code: str
    backend_code: str

    # 测试工程师输出
    test_cases: str
    test_result: str

    # 验收
    review_result: str
    review_passed: bool

    # 流程控制
    iteration_count: int
    max_iterations: int
    current_phase: str

    # 历史
    messages: Annotated[list[dict], add]

    # 人工介入标记
    needs_human_approval: bool
    human_feedback: str


# =============================================================================
# 扩展代理
# =============================================================================

class ProductManager:
    """产品经理代理。"""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.llm = ChatAnthropic(model=model, temperature=0.7)

    def create_prd(self, state: ExtendedFeatureState) -> dict:
        """创建产品需求文档。"""
        messages = [
            SystemMessage(content="你是产品经理，负责将用户需求转化为详细的产品需求文档。"),
            HumanMessage(content=f"""
请根据以下需求创建产品需求文档（PRD）：

{state['requirement']}

请包含：
1. 功能概述
2. 用户故事
3. 功能清单
4. 非功能需求
5. 验收标准
            """),
        ]

        response = self.llm.invoke(messages)

        return {
            "prd": response.content,
            "current_phase": "prd_created",
            "messages": [{"role": "pm", "content": response.content}],
        }


class TestEngineer:
    """测试工程师代理。"""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.llm = ChatAnthropic(model=model, temperature=0.3)

    def create_test_cases(self, state: ExtendedFeatureState) -> dict:
        """创建测试用例。"""
        messages = [
            SystemMessage(content="你是测试工程师，负责根据需求和设计创建测试用例。"),
            HumanMessage(content=f"""
请根据以下内容创建测试用例：

## PRD
{state['prd']}

## 设计
{state['design_spec']}

请创建：
1. 单元测试用例
2. 集成测试用例
3. 端到端测试用例
4. 边界测试用例
            """),
        ]

        response = self.llm.invoke(messages)

        return {
            "test_cases": response.content,
            "current_phase": "test_cases_created",
            "messages": [{"role": "tester", "content": response.content}],
        }

    def run_tests(self, state: ExtendedFeatureState) -> dict:
        """执行测试（模拟）。"""
        messages = [
            SystemMessage(content="你是测试工程师，请评估代码是否通过测试用例。"),
            HumanMessage(content=f"""
## 测试用例
{state['test_cases']}

## 前端代码
{state['frontend_code']}

## 后端代码
{state['backend_code']}

请执行测试并给出结果，格式：
- 通过的测试
- 失败的测试
- 总体结论（通过/不通过）
            """),
        ]

        response = self.llm.invoke(messages)

        return {
            "test_result": response.content,
            "current_phase": "tests_executed",
            "messages": [{"role": "tester", "content": response.content}],
        }


# =============================================================================
# 构建高级工作流
# =============================================================================

def build_advanced_graph(with_checkpointer: bool = True):
    """
    构建高级工作流图。

    流程：
    PM(PRD) → 设计师(设计) → [前端开发, 后端开发](并行) → 测试 → 验收 → 结束
    """
    from langgraph_1.agents import InteractionDesigner, Developer

    # 初始化代理
    pm = ProductManager()
    designer = InteractionDesigner()
    frontend_dev = Developer()
    backend_dev = Developer()
    tester = TestEngineer()

    # 创建图
    graph = StateGraph(ExtendedFeatureState)

    # 添加节点
    graph.add_node("pm", pm.create_prd)
    graph.add_node("design", lambda s: designer.design(s))
    graph.add_node("frontend", lambda s: {"frontend_code": frontend_dev.implement(s)["code"]})
    graph.add_node("backend", lambda s: {"backend_code": backend_dev.implement(s)["code"]})
    graph.add_node("test_cases", tester.create_test_cases)
    graph.add_node("test_run", tester.run_tests)
    graph.add_node("review", lambda s: designer.review(s))

    # 设置入口
    graph.set_entry_point("pm")

    # 添加边
    graph.add_edge("pm", "design")
    graph.add_edge("design", "test_cases")

    # 并行开发（设计完成后同时开始前后端）
    graph.add_edge("design", "frontend")
    graph.add_edge("design", "backend")

    # 开发完成后测试
    graph.add_edge("frontend", "test_run")
    graph.add_edge("backend", "test_run")
    graph.add_edge("test_cases", "test_run")

    # 测试后验收
    graph.add_edge("test_run", "review")

    # 验收后的路由
    def review_router(state: ExtendedFeatureState) -> Literal["frontend", "end"]:
        if state.get("review_passed", False):
            return "end"
        if state.get("iteration_count", 0) >= state.get("max_iterations", 3):
            return "end"
        return "frontend"

    graph.add_conditional_edges("review", review_router, {
        "frontend": "frontend",
        "end": END,
    })

    # 编译
    if with_checkpointer:
        checkpointer = MemorySaver()
        return graph.compile(checkpointer=checkpointer)
    else:
        return graph.compile()


# =============================================================================
# Human-in-the-loop 示例
# =============================================================================

def build_hitl_graph():
    """
    构建带人工介入的工作流。

    在关键节点暂停等待人工审批。
    """
    from langgraph_1.agents import InteractionDesigner, Developer

    designer = InteractionDesigner()
    developer = Developer()

    graph = StateGraph(ExtendedFeatureState)

    # 添加节点
    graph.add_node("design", lambda s: designer.design(s))
    graph.add_node("human_review_design", lambda s: s)  # 等待人工审批
    graph.add_node("develop", lambda s: developer.implement(s))
    graph.add_node("human_review_code", lambda s: s)  # 等待人工审批
    graph.add_node("final_review", lambda s: designer.review(s))

    # 设置流程
    graph.set_entry_point("design")
    graph.add_edge("design", "human_review_design")
    graph.add_edge("human_review_design", "develop")
    graph.add_edge("develop", "human_review_code")
    graph.add_edge("human_review_code", "final_review")
    graph.add_edge("final_review", END)

    # 使用 checkpointer 支持暂停
    checkpointer = MemorySaver()

    # 在人工审批节点设置中断
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review_design", "human_review_code"],
    )


# =============================================================================
# 示例运行
# =============================================================================

def run_with_checkpointer():
    """演示使用 Checkpointer 保存和恢复状态。"""
    print("=" * 60)
    print("Checkpointer 示例")
    print("=" * 60)

    graph = build_advanced_graph(with_checkpointer=True)

    # 第一次运行
    config = {"configurable": {"thread_id": "project-123"}}

    initial_state = {
        "requirement": "创建一个简单的博客系统",
        "prd": "",
        "design_spec": "",
        "frontend_code": "",
        "backend_code": "",
        "test_cases": "",
        "test_result": "",
        "review_result": "",
        "review_passed": False,
        "iteration_count": 0,
        "max_iterations": 2,
        "current_phase": "start",
        "messages": [],
        "needs_human_approval": False,
        "human_feedback": "",
    }

    print("\n开始执行...")

    for event in graph.stream(initial_state, config):
        for node, output in event.items():
            print(f"[{node}] 完成")

    # 可以在此处保存 thread_id，稍后恢复
    print(f"\n状态已保存到 thread_id: project-123")
    print("可以使用相同的 thread_id 恢复执行")


def run_hitl_example():
    """演示人工介入流程。"""
    print("=" * 60)
    print("Human-in-the-loop 示例")
    print("=" * 60)

    graph = build_hitl_graph()

    config = {"configurable": {"thread_id": "hitl-demo"}}

    initial_state = {
        "requirement": "创建用户注册功能",
        "prd": "",
        "design_spec": "",
        "frontend_code": "",
        "backend_code": "",
        "test_cases": "",
        "test_result": "",
        "review_result": "",
        "review_passed": False,
        "iteration_count": 0,
        "max_iterations": 2,
        "current_phase": "start",
        "messages": [],
        "needs_human_approval": False,
        "human_feedback": "",
    }

    print("\n开始执行（会在人工审批节点暂停）...")

    # 执行直到暂停
    for event in graph.stream(initial_state, config):
        for node, output in event.items():
            print(f"[{node}] 完成")

    print("\n工作流已暂停，等待人工审批...")
    print("使用 graph.invoke(None, config) 继续执行")


if __name__ == "__main__":
    import sys

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("请设置 ANTHROPIC_API_KEY 环境变量")
        sys.exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] == "checkpointer":
            run_with_checkpointer()
        elif sys.argv[1] == "hitl":
            run_hitl_example()
        else:
            print("用法: python advanced_workflow.py [checkpointer|hitl]")
    else:
        run_with_checkpointer()
