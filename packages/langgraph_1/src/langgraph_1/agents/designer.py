"""
交互设计师代理。

负责：
1. 根据需求创建交互设计
2. 验收开发成果是否符合设计
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic

from ..state import FeatureState
from ..prompts import DESIGNER_SYSTEM_PROMPT, DESIGN_PROMPT, REVIEW_PROMPT


class InteractionDesigner:
    """交互设计师代理。"""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """
        初始化交互设计师。

        Args:
            model: 使用的模型名称
        """
        self.llm = ChatAnthropic(model=model, temperature=0.7)

    def design(self, state: FeatureState) -> dict:
        """
        设计阶段：根据需求创建交互设计。

        Args:
            state: 当前状态

        Returns:
            更新后的状态字段
        """
        messages = [
            SystemMessage(content=DESIGNER_SYSTEM_PROMPT),
            HumanMessage(content=DESIGN_PROMPT.format(
                requirement=state["requirement"]
            )),
        ]

        response = self.llm.invoke(messages)
        design_content = response.content

        # 解析设计内容（简化处理，实际可用结构化输出）
        return {
            "design_spec": design_content,
            "user_flow": self._extract_section(design_content, "用户流程"),
            "ui_layout": self._extract_section(design_content, "界面布局"),
            "interaction_details": self._extract_section(design_content, "交互细节"),
            "messages": [{
                "role": "designer",
                "phase": "design",
                "content": design_content,
            }],
        }

    def review(self, state: FeatureState) -> dict:
        """
        验收阶段：检查开发成果是否符合设计。

        Args:
            state: 当前状态

        Returns:
            更新后的状态字段
        """
        messages = [
            SystemMessage(content=DESIGNER_SYSTEM_PROMPT),
            HumanMessage(content=REVIEW_PROMPT.format(
                design_spec=state["design_spec"],
                code=state["code"],
            )),
        ]

        response = self.llm.invoke(messages)
        review_content = response.content

        # 判断是否通过
        passed = self._check_passed(review_content)

        result = {
            "review_result": review_content,
            "review_passed": passed,
            "iteration_count": state["iteration_count"] + 1,
            "messages": [{
                "role": "designer",
                "phase": "review",
                "content": review_content,
                "passed": passed,
            }],
        }

        # 如果未通过，添加反馈
        if not passed:
            result["feedback"] = [self._extract_feedback(review_content)]

        return result

    def _extract_section(self, content: str, section_name: str) -> str:
        """从设计内容中提取指定章节。"""
        lines = content.split("\n")
        in_section = False
        section_lines = []

        for line in lines:
            if section_name in line:
                in_section = True
                continue
            if in_section:
                # 遇到下一个章节标题时停止
                if line.startswith("#") or line.startswith("##"):
                    break
                section_lines.append(line)

        return "\n".join(section_lines).strip()

    def _check_passed(self, review_content: str) -> bool:
        """检查验收是否通过。"""
        content_lower = review_content.lower()
        # 检查明确的通过/不通过标记
        if "不通过" in review_content or "未通过" in review_content:
            return False
        if "通过" in review_content:
            return True
        # 检查英文标记
        if "rejected" in content_lower or "not approved" in content_lower:
            return False
        if "approved" in content_lower or "passed" in content_lower:
            return True
        return False

    def _extract_feedback(self, review_content: str) -> str:
        """从验收结果中提取反馈。"""
        # 简化处理：返回整个验收结果作为反馈
        # 实际可以更精细地提取问题列表
        return review_content
