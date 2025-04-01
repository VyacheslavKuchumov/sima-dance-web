
class WebSocketService {
    constructor() {
      this.url = process.env.VUE_APP_SERVER + "/ws";
      this.socket = null;
    }
  
    connect() {
      this.socket = new WebSocket(this.url);
  
      // Optional: return a promise that resolves when the connection is open
      return new Promise((resolve, reject) => {
        this.socket.onopen = () => {
          console.log("WebSocket connection opened");
          resolve();
        };
        this.socket.onerror = (error) => {
          console.error("WebSocket error:", error);
          reject(error);
        };
      });
    }
  
    onMessage(callback) {
      if (this.socket) {
        this.socket.onmessage = (event) => {
          callback(event.data);
        };
      }
    }
    disconnect() {
      if (this.socket) {
        this.socket.close();
        console.log("WebSocket connection closed");
      }
    }
  
    send(message) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(message);
      } else {
        console.error("WebSocket is not open. Cannot send message.");
      }
    }
  
    onClose(callback) {
      if (this.socket) {
        this.socket.onclose = (event) => {
          console.log("WebSocket connection closed:", event);
          callback(event);
        };
      }
    }
  }
  
  export default WebSocketService;