# LangGraph 多代理协作示例

本包演示如何使用 LangGraph 构建多代理协作系统，模拟真实的软件开发流程。

## 核心场景：功能开发工作流

```
需求输入 → 交互设计师(设计) → 开发工程师(开发) → 交互设计师(验收)
                                                      ↓
                                              通过 → 完成
                                              不通过 → 返回开发修改
```

## 角色定义

| 角色 | 职责 | 输入 | 输出 |
|------|------|------|------|
| 交互设计师 | 设计交互方案 | 需求描述 | 交互设计稿 |
| 开发工程师 | 实现功能代码 | 设计稿 + 反馈 | 功能代码 |
| 交互设计师 | 验收开发成果 | 设计稿 + 代码 | 验收结果 |

## 安装

```bash
pip install langgraph langchain-anthropic
```

## 快速开始

```python
from langgraph_1 import FeatureDevelopmentGraph

# 创建工作流
workflow = FeatureDevelopmentGraph()

# 执行开发流程
result = workflow.run({
    "requirement": "设计一个用户登录页面，支持手机号和邮箱登录"
})

print(result["design_spec"])  # 交互设计
print(result["code"])         # 开发代码
print(result["review_result"]) # 验收结果
```

## 项目结构

```
langgraph_1/
├── src/langgraph_1/
│   ├── __init__.py
│   ├── state.py          # 状态定义
│   ├── agents/           # 代理实现
│   │   ├── __init__.py
│   │   ├── designer.py   # 交互设计师
│   │   └── developer.py  # 开发工程师
│   ├── graph.py          # 工作流图定义
│   └── prompts.py        # 提示词模板
├── examples/
│   ├── basic_workflow.py # 基础示例
│   └── advanced_workflow.py # 高级示例
├── pyproject.toml
└── README.md
```

## 扩展方向

1. **增加更多角色** - 产品经理、测试工程师、技术负责人
2. **并行任务** - 前端/后端同时开发
3. **人工介入** - 关键节点等待人工审批
4. **持久化状态** - 使用 checkpointer 保存项目进度
5. **可视化** - 集成 LangGraph Studio 查看执行过程
