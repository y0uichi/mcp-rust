# MetaGPT 深度分析

## 概述

MetaGPT是最适合本项目的框架，因为它本身就是为模拟软件公司协作而设计的。

## 核心理念

**"Code = SOP(Team)"** - 代码是团队按照标准操作流程协作的产物

## 架构特点

### 1. 角色分配

MetaGPT内置以下角色：
- **Product Manager** (产品经理) - 需求分析、用户故事
- **Architect** (架构师) - 系统设计、技术选型
- **Project Manager** (项目经理) - 任务分解、进度管理
- **Engineer** (工程师) - 代码实现
- **Tester** (测试工程师) - 测试用例、验收测试

### 2. 结构化通信

与其他框架不同，MetaGPT使用**结构化输出**（文档、图表）而非自由对话进行Agent间通信。

优势：
- 减少歧义
- 便于验证中间结果
- 更接近真实工作流程

### 3. SOP编码

将标准操作流程编码到Prompt序列中：
- 每个角色有明确的输入输出规范
- 自动验证中间产物
- 减少错误传播

## 工作流程

```
需求输入 → 产品经理(PRD) → 架构师(设计文档) → 工程师(代码) → 测试工程师(测试) → 交付
```

## 与本项目的对应关系

| 项目角色 | MetaGPT角色 | 产出物 |
|----------|-------------|--------|
| 交互设计师 | Product Manager + 自定义 | 交互文档 |
| 测试工程师 | Tester | 测试用例文档 |
| 开发工程师 | Engineer | 代码 |

## 最新发展

- **2025年2月**: 推出 MGX (MetaGPT X) - 世界上第一个AI Agent开发团队产品
- **ICLR 2025**: "AFlow: Automating Agentic Workflow Generation" 论文获口头报告 (top 1.8%)

## 参考资料

- [MetaGPT GitHub](https://github.com/FoundationAgents/MetaGPT)
- [MetaGPT Documentation](https://docs.deepwisdom.ai/main/en/guide/get_started/introduction.html)
- [What is MetaGPT - IBM](https://www.ibm.com/think/topics/metagpt)
- [MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework](https://arxiv.org/abs/2308.00352)
