const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

class ChatService {
  constructor() {
    this.ws = null;
    this.gameId = null;
    this.messageCallbacks = [];
  }

  connect(gameId, username, userId) {
    this.gameId = gameId;
    this.ws = new WebSocket(`${WS_URL}/ws/chat/${gameId}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.messageCallbacks.forEach(callback => callback(message));
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    this.username = username;
    this.userId = userId;
  }

  sendMessage(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        username: this.username,
        user_id: this.userId,
        message: message
      }));
    }
  }

  onMessage(callback) {
    this.messageCallbacks.push(callback);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.messageCallbacks = [];
  }
}

export default new ChatService();
