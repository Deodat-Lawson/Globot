import { chatAPI } from './api';

/**
 * Message Service Abstraction Layer - Supports HTTP Polling and WebSocket switching
 */

// Polling Strategy (used in MVP)
export class PollingStrategy {
  subscribe(customerId, callback) {
    const interval = setInterval(async () => {
      try {
        const response = await chatAPI.getConversations(customerId);
        callback(response.data);
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 5000); // Poll every 5 seconds

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

// WebSocket Strategy (V1.0 - Reserved Interface)
export class WebSocketStrategy {
  constructor() {
    this.connections = new Map();
  }

  subscribe(customerId, callback) {
    // TODO: V1.0 implementation
    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}/${customerId}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(data);
    };

    ws.onerror = (error) => {
      console.warn('WebSocket error, falling back to polling', error);
      // Fallback to polling
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

// Message Service - Unified Interface
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

// Default export: Message Service with Polling Strategy
export default new MessageService(new PollingStrategy());
