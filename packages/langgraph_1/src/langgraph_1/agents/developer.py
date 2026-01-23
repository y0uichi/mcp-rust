"""
开发工程师代理。

负责：
1. 根据交互设计实现功能代码
2. 根据验收反馈修改代码
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic

from ..state import FeatureState
from ..prompts import DEVELOPER_SYSTEM_PROMPT, DEVELOP_PROMPT, REVISE_PROMPT


class Developer:
    """开发工程师代理。"""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """
        初始化开发工程师。

        Args:
            model: 使用的模型名称
        """
        self.llm = ChatAnthropic(model=model, temperature=0.3)

    def implement(self, state: FeatureState) -> dict:
        """
        开发阶段：根据设计稿实现功能。

        Args:
            state: 当前状态

        Returns:
            更新后的状态字段
        """
        # 检查是否是首次开发还是修改
        if state["iteration_count"] == 0:
            return self._initial_implement(state)
        else:
            return self._revise_implement(state)

    def _initial_implement(self, state: FeatureState) -> dict:
        """首次开发实现。"""
        messages = [
            SystemMessage(content=DEVELOPER_SYSTEM_PROMPT),
            HumanMessage(content=DEVELOP_PROMPT.format(
                design_spec=state["design_spec"],
                user_flow=state["user_flow"],
                ui_layout=state["ui_layout"],
                interaction_details=state["interaction_details"],
            )),
        ]

        response = self.llm.invoke(messages)
        code_content = response.content

        return {
            "code": code_content,
            "messages": [{
                "role": "developer",
                "phase": "implement",
                "iteration": state["iteration_count"],
                "content": code_content,
            }],
        }

    def _revise_implement(self, state: FeatureState) -> dict:
        """根据反馈修改实现。"""
        # 获取最新的反馈
        latest_feedback = state["feedback"][-1] if state["feedback"] else ""

        messages = [
            SystemMessage(content=DEVELOPER_SYSTEM_PROMPT),
            HumanMessage(content=REVISE_PROMPT.format(
                design_spec=state["design_spec"],
                previous_code=state["code"],
                feedback=latest_feedback,
                all_feedback="\n---\n".join(state["feedback"]),
            )),
        ]

        response = self.llm.invoke(messages)
        code_content = response.content

        return {
            "code": code_content,
            "messages": [{
                "role": "developer",
                "phase": "revise",
                "iteration": state["iteration_count"],
                "content": code_content,
            }],
        }
