# DJI Sales AI Assistant - Frontend

前端界面，包含客户聊天 Widget 和管理后台。

## 技术栈

- **React** 18
- **Ant Design** 5
- **Vite** 5
- **React Router** 6
- **Axios**

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:5173

### 构建生产版本

```bash
npm run build
```

## 页面说明

### 客户端

- **首页** (`/`) - 包含 Chat Widget 浮动聊天窗口
- 客户可以直接在网页上与 AI 对话

### 管理后台

- **客户列表** (`/admin/customers`) - 查看所有客户，按优先级排序
- **对话详情** (`/admin/conversations/:id`) - 查看具体客户的对话历史

## 功能特性

### Chat Widget

- ✅ 浮动聊天按钮
- ✅ 实时对话
- ✅ Markdown 渲染
- ✅ 消息轮询（5 秒）
- ✅ 响应式设计

### Admin Dashboard

- ✅ 客户列表表格
- ✅ 搜索和排序
- ✅ 客户分类标签（高价值/普通/低价值）
- ✅ 对话历史 Timeline
- ✅ 置信度显示

## 配置

### 环境变量

创建 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws  # V1.0使用
```

## 架构特点

### 消息服务抽象层

使用适配器模式，便于从 HTTP 轮询升级到 WebSocket：

```javascript
// MVP: HTTP轮询
const messageService = new MessageService(new PollingStrategy());

// V1.0: WebSocket（只需修改1行）
const messageService = new MessageService(new WebSocketStrategy());
```

### API 服务层

统一的 API 调用接口，便于管理和测试。

## 目录结构

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget/       # 客户聊天组件
│   │   └── Admin/            # 管理后台组件
│   ├── services/
│   │   ├── api.js            # API调用
│   │   └── messageService.js # 消息服务抽象
│   ├── App.jsx               # 主应用
│   └── main.jsx              # 入口
├── package.json
└── vite.config.js
```

## 开发说明

### 添加新页面

1. 在 `src/components` 创建组件
2. 在 `App.jsx` 添加路由

### 调用 API

```javascript
import { chatAPI } from "./services/api";

const response = await chatAPI.sendMessage({
  customer_id: 1,
  message: "M30的续航时间？",
});
```

---

**版本**: 1.0.0  
**状态**: ✅ 开发完成
