# 🛡️ Globot: 全球贸易的 AI 守护盾 (v2.3.20260124)

> **Imagine Cup 2026 参赛作品 - "High-Fidelity Demo (高保真演示)" 版本**

![Globot Dashboard](ai-sales-mvp/frontend/src/assets/dashboard_preview.png)

## 📖 项目概览

**Globot** 代表了全球贸易风险管理的范式转变。与传统的静态仪表盘不同，Globot 是一个 **Agentic AI (代理智能) 系统**，能够实时主动监控、分析并缓解供应链风险。

此版本 (**v2.3.20260124 - 地图重绘特别版**) 是专门构建的 **"High-Fidelity Mock (高保真模拟)"** 版本。本次更新核心在于 **2D/3D 地图引擎的全面重构**，引入了影院级的视觉效果、丝滑的交互体验和精确的地理参考系统。

## 🌟 核心功能 (v2.1 升级版)

### 1. 🧠 可视化 AI 思维链 (Chain-of-Thought)

- **实时推理展示**: 像 "打字机" 一样逐行展示 AI 的思考过程，不再是黑盒。
- **多 Agent 辩论**: 展示 "红队 vs 蓝队" 的对抗性辩论 (Adversarial Debate)，确保决策鲁棒性。
- **引用溯源**: 每个推理步骤都关联到具体的 RAG 知识库文档或实时新闻源。

### 2. 🤖 多 Agent 协作引擎

展示了由 5 个专业 AI Agent 组成的团队协同工作：

- **🔭 市场哨兵 (Market Sentinel)**: 监控路透社/彭博社的地缘政治信号 (Mock API 支持多场景：红海危机、港口拥堵等)。
- **🛡️ 风险对冲专家 (Risk Hedger)**: 计算财务风险敞口并触发保险买入。
- **🚢 物流指挥官 (Logistics Orchestrator)**: 重新规划航线以避开冲突区域。
- **📋 合规经理 (Compliance Manager)**: 核查 OFAC/UN 制裁名单。
- **⚖️ 对抗性辩论 (Adversarial Debate)**: 对决策进行红队测试，防止幻觉。

### 3. 🛫 航空级物流全息地图 (Deck.gl)

- **线路与港口**: 可视化全球主要航线及上海、鹿特丹、洛杉矶等核心港口。
- **交互式船舶**: 点击地图上的黄色船舶图标，可查看详细货物清单和航行状态。
- **动态风险**: 危机发生时，受影响区域会高亮并发出脉冲警报。

### 4. 👨‍✈️ 人机共驾 (Human-in-the-Loop)

- **决策确认**: AI 提出建议后，必须由人类点击 **"Approve & Execute"** 才能执行，体现负责任的 AI 原则。
- **多种选择**: 提供 "Details" (查看详情) 和 "Override" (人工干预) 选项。

### 5. 📚 智能知识库 (RAG Knowledge Base)

- **Globot System KB**: 加载结构化知识库索引作为 Agent 的 System Prompt，指导 RAG 检索。
- **Mock 数据集成**: 内置 24 个核心文档（HS Codes、Incoterms、Sanctions、Port Congestion、Freight Rates、Carrier Routes）。
- **自动加载**: 后端启动时自动将 Mock 文档加载到 VectorStore，无需手动配置。

### 6. 🌍 地图引擎重构 (v2.3 新增)

- **2D/3D 一体化**: 全面升级 `GlobalMap2D` 和 `GlobalMap3D` 组件，视觉风格高度统一。
- **交互优化**: 
    - **3D**: 修复了 Z-fighting 屏闪问题，实现了丝滑的惯性缩放和左键旋转 (`dragPan`)。
    - **2D**: 实现了标签智能防重叠 (`CollisionFilter`)，从根本上解决了密集区域文字遮挡问题。
- **视觉增强**:
    - **经纬网格**: 新增半透明白色经纬线及数字标签，提供精确地理参考。
    - **标签分级**: 港口、海峡、国家名称采用统一的配色（红/橙/白）和粗体样式，层级分明。
    - **动态参数**: 支持实时调节 Label Size 和 Ship Speed (范围扩展至 5-50)，满足不同演示需求。

## 🏗️ 技术架构 (演示专用版)

```mermaid
graph TD
    Client[前端 (React + Vite)]
    MockServer[后端 (FastAPI + High-Fidelity Mock)]

    subgraph "前端层 (UI/UX)"
        Map[3D/2D 地球 (Deck.gl)]
        CoT[思维链面板 (WebSocket)]
        Nav[航线选择器 (/port)]
    end

    subgraph "后端逻辑 (Python)"
        WS[WebSocket 事件流]
        Sentinel[市场哨兵 Mock 服务]
        Controller[自动播放控制器]
    end

    Client <-->|CoT Events / Actions| WS
    WS <--> Controller
    Controller -->|调用| Sentinel
```

- **前端**: React, TypeScript, Tailwind CSS, Deck.gl, Framer Motion.
- **后端**: Python FastAPI, WebSocket (实现双向实时通信).
- **主要流程**: `/pay` (营销页) -> `/port` (航线选择) -> `/demo` (核心模拟).

## 🚀 快速开始

### 1. 启动后端

```bash
cd backend
# 确保安装了依赖
# pip install -r requirements.txt
python start_server.py
```
_后端运行在 `http://localhost:8000`_

### 2. 启动前端

```bash
cd frontend
npm run dev
```
_前端运行在 `http://localhost:5173`_

### 3. 演示路径

1. 打开浏览器访问: `http://localhost:5173/pay`
2. 点击 **"Watch Demo"**，跳转至航线选择页 (`/port`)。
3. 确认路线（默认 Shanghai -> Rotterdam），点击 **"Start Simulation"** 进入演示 (`/demo`)。
4. 观察 AI 推理过程，待 "Approve & Execute" 按钮出现后点击确认。

## 📂 关键文件说明

- `操作指南.md`: 详细的演示操作步骤说明（新用户必读）。
- `task.md`: 项目开发任务清单。
- `开关.md`: 服务启动与故障排查速查表。
- `Globot System Knowledge Base.JSON`: Agent 知识库索引（用于 System Prompt）。
- `HS_Code_Mocktest.JSON`: HS Code 关税 Mock 数据。
- `backend/services/mock_knowledge_base.py`: Mock 数据加载服务。
- `backend/services/knowledge_base.py`: RAG 知识库核心服务（含 `get_globot_system_prompt()` 函数）。

---

**维护者**: Vector897
**许可证**: MIT
