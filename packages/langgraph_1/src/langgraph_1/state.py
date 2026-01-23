"""
状态定义模块。

定义工作流中共享的状态结构。
"""

from typing import TypedDict, Annotated
from operator import add


class FeatureState(TypedDict):
    """功能开发工作流的状态。"""

    # 输入
    requirement: str
    """需求描述"""

    # 设计阶段输出
    design_spec: str
    """交互设计规范"""

    user_flow: str
    """用户流程"""

    ui_layout: str
    """界面布局"""

    interaction_details: str
    """交互细节"""

    # 开发阶段输出
    code: str
    """实现代码"""

    # 验收阶段
    review_result: str
    """验收结果"""

    review_passed: bool
    """是否通过验收"""

    # 流程控制
    iteration_count: int
    """迭代次数"""

    max_iterations: int
    """最大迭代次数"""

    # 历史记录（使用 Annotated 支持累加）
    feedback: Annotated[list[str], add]
    """反馈历史，每次验收不通过时累加"""

    messages: Annotated[list[dict], add]
    """消息历史，记录所有交互"""


def create_initial_state(requirement: str, max_iterations: int = 3) -> FeatureState:
    """
    创建初始状态。

    Args:
        requirement: 需求描述
        max_iterations: 最大迭代次数，默认3次

    Returns:
        初始化的 FeatureState
    """
    return FeatureState(
        requirement=requirement,
        design_spec="",
        user_flow="",
        ui_layout="",
        interaction_details="",
        code="",
        review_result="",
        review_passed=False,
        iteration_count=0,
        max_iterations=max_iterations,
        feedback=[],
        messages=[],
    )
