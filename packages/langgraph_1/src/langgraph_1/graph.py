"""
工作流图定义模块。

使用 LangGraph 定义功能开发的工作流程。
"""

from typing import Literal

from langgraph.graph import StateGraph, END

from .state import FeatureState, create_initial_state
from .agents import InteractionDesigner, Developer


class FeatureDevelopmentGraph:
    """
    功能开发工作流图。

    工作流程：
    1. 交互设计师根据需求创建设计
    2. 开发工程师根据设计实现代码
    3. 交互设计师验收开发成果
    4. 如不通过，返回步骤2修改；如通过，结束

    ```
    需求 → [设计] → [开发] → [验收] → 通过? → 结束
                       ↑         ↓
                       ←── 不通过 ←
    ```
    """

    def __init__(
        self,
        designer_model: str = "claude-sonnet-4-20250514",
        developer_model: str = "claude-sonnet-4-20250514",
    ):
        """
        初始化工作流图。

        Args:
            designer_model: 交互设计师使用的模型
            developer_model: 开发工程师使用的模型
        """
        self.designer = InteractionDesigner(model=designer_model)
        self.developer = Developer(model=developer_model)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建工作流图。"""
        # 创建状态图
        graph = StateGraph(FeatureState)

        # 添加节点
        graph.add_node("design", self._design_node)
        graph.add_node("develop", self._develop_node)
        graph.add_node("review", self._review_node)

        # 设置入口点
        graph.set_entry_point("design")

        # 添加边
        graph.add_edge("design", "develop")
        graph.add_edge("develop", "review")

        # 添加条件边（验收后的路由）
        graph.add_conditional_edges(
            "review",
            self._review_router,
            {
                "revise": "develop",  # 不通过，返回开发
                "complete": END,       # 通过，结束
            },
        )

        return graph.compile()

    def _design_node(self, state: FeatureState) -> dict:
        """设计节点：交互设计师创建设计。"""
        return self.designer.design(state)

    def _develop_node(self, state: FeatureState) -> dict:
        """开发节点：开发工程师实现代码。"""
        return self.developer.implement(state)

    def _review_node(self, state: FeatureState) -> dict:
        """验收节点：交互设计师验收成果。"""
        return self.designer.review(state)

    def _review_router(self, state: FeatureState) -> Literal["revise", "complete"]:
        """
        验收后的路由逻辑。

        Args:
            state: 当前状态

        Returns:
            "revise" 如果需要修改，"complete" 如果通过
        """
        # 检查是否通过验收
        if state["review_passed"]:
            return "complete"

        # 检查是否超过最大迭代次数
        if state["iteration_count"] >= state["max_iterations"]:
            print(f"达到最大迭代次数 ({state['max_iterations']})，强制结束")
            return "complete"

        return "revise"

    def run(
        self,
        requirement: str,
        max_iterations: int = 3,
    ) -> FeatureState:
        """
        运行工作流。

        Args:
            requirement: 需求描述
            max_iterations: 最大迭代次数

        Returns:
            最终状态
        """
        initial_state = create_initial_state(
            requirement=requirement,
            max_iterations=max_iterations,
        )

        # 执行图
        result = self.graph.invoke(initial_state)
        return result

    async def arun(
        self,
        requirement: str,
        max_iterations: int = 3,
    ) -> FeatureState:
        """
        异步运行工作流。

        Args:
            requirement: 需求描述
            max_iterations: 最大迭代次数

        Returns:
            最终状态
        """
        initial_state = create_initial_state(
            requirement=requirement,
            max_iterations=max_iterations,
        )

        # 异步执行图
        result = await self.graph.ainvoke(initial_state)
        return result

    def stream(
        self,
        requirement: str,
        max_iterations: int = 3,
    ):
        """
        流式运行工作流，返回每个节点的输出。

        Args:
            requirement: 需求描述
            max_iterations: 最大迭代次数

        Yields:
            (节点名, 状态更新) 元组
        """
        initial_state = create_initial_state(
            requirement=requirement,
            max_iterations=max_iterations,
        )

        # 流式执行
        for event in self.graph.stream(initial_state):
            yield event

    def get_graph_image(self):
        """
        获取工作流图的可视化。

        Returns:
            PNG 图像数据
        """
        return self.graph.get_graph().draw_mermaid_png()
