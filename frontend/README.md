# DJI Sales AI Assistant - Frontend

Frontend interface, including customer chat widget and admin dashboard.

## Tech Stack

- **React** 18
- **Ant Design** 5
- **Vite** 5
- **React Router** 6
- **Axios**

## Quick Start

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

Visit: http://localhost:5173

### Build Production Version

```bash
npm run build
```

## Page Description

### Client Side

- **Home** (`/`) - Includes the Chat Widget floating chat window
- Customers can directly chat with AI on the webpage

### Admin Dashboard

- **Customer List** (`/admin/customers`) - View all customers, sorted by priority
- **Conversation Details** (`/admin/conversations/:id`) - View specific customer's conversation history

## Features

### Chat Widget

- ✅ Floating chat button
- ✅ Real-time conversation
- ✅ Markdown rendering
- ✅ Message polling (5 seconds)
- ✅ Responsive design

### Admin Dashboard

- ✅ Customer list table
- ✅ Search and sort
- ✅ Customer category tags (High Value / Normal / Low Value)
- ✅ Conversation history Timeline
- ✅ Confidence display

## Configuration

### Environment Variables

Create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws  # For V1.0 usage
```

## Architectural Highlights

### Message Service Abstraction Layer

Uses the Adapter pattern for easy upgrades from HTTP polling to WebSocket:

```javascript
// MVP: HTTP Polling
const messageService = new MessageService(new PollingStrategy());

// V1.0: WebSocket (only requires 1 line change)
const messageService = new MessageService(new WebSocketStrategy());
```

### API Service Layer

Unified API invocation interface for easier management and testing.

## Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget/       # Customer chat components
│   │   └── Admin/            # Admin dashboard components
│   ├── services/
│   │   ├── api.js            # API calls
│   │   └── messageService.js # Message service abstraction
│   ├── App.jsx               # Main application
│   └── main.jsx              # Entry point
├── package.json
└── vite.config.js
```

## Development Notes

### Adding a New Page

1. Create a component in `src/components`
2. Add a route in `App.jsx`

### Calling API

```javascript
import { chatAPI } from "./services/api";

const response = await chatAPI.sendMessage({
  customer_id: 1,
  message: "M30 battery life?",
});
```

---

**Version**: 1.0.0  
**Status**: ✅ Development Complete
