import { chatAPI } from './api';

/**
 * 消息服务抽象层 - 支持HTTP轮询和WebSocket切换
 */

// 轮询策略（MVP使用）
export class PollingStrategy {
  subscribe(customerId, callback) {
    const interval = setInterval(async () => {
      try {
        const response = await chatAPI.getConversations(customerId);
        callback(response.data);
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 5000); // 每5秒轮询一次
    
    return {
      type: 'polling',
      interval,
      unsubscribe: () => clearInterval(interval)
    };
  }
  
  unsubscribe(subscription) {
    if (subscription && subscription.unsubscribe) {
      subscription.unsubscribe();
    }
  }
}

// WebSocket策略（V1.0使用 - 预留接口）
export class WebSocketStrategy {
  constructor() {
    this.connections = new Map();
  }
  
  subscribe(customerId, callback) {
    // TODO: V1.0实现
    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}/${customerId}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(data);
    };
    
    ws.onerror = (error) => {
      console.warn('WebSocket error, falling back to polling', error);
      // 降级到轮询
      const pollingStrategy = new PollingStrategy();
      return pollingStrategy.subscribe(customerId, callback);
    };
    
    this.connections.set(customerId, ws);
    
    return {
      type: 'websocket',
      ws,
      unsubscribe: () => {
        ws.close();
        this.connections.delete(customerId);
      }
    };
  }
  
  unsubscribe(subscription) {
    if (subscription && subscription.unsubscribe) {
      subscription.unsubscribe();
    }
  }
}

// 消息服务 - 统一接口
export class MessageService {
  constructor(strategy = new PollingStrategy()) {
    this.strategy = strategy;
  }
  
  subscribe(customerId, callback) {
    return this.strategy.subscribe(customerId, callback);
  }
  
  unsubscribe(subscription) {
    this.strategy.unsubscribe(subscription);
  }
  
  setStrategy(strategy) {
    this.strategy = strategy;
  }
}

// 默认导出轮询策略的消息服务
export default new MessageService(new PollingStrategy());
