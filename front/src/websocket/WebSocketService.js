class WebSocketService {
  constructor() {
    this.url = process.env.VUE_APP_SERVER + "/ws";
    this.socket = null;
    this.forcedClose = false;             // When true, stops reconnection attempts.
    this.reconnectInterval = 5000;          // Initial reconnection delay (in ms).
    this.maxReconnectInterval = 30000;      // Maximum allowed reconnection delay.
    this.reconnectDecay = 1.5;              // Factor by which the interval increases.
    this.timeoutId = null;                // Stores the timeout ID for reconnection.
    this.customOnClose = null;            // Optional custom onClose callback.
  }

  connect() {
    // Reset forcedClose flag if connect is called after a disconnect.
    this.forcedClose = false;
    this.socket = new WebSocket(this.url);

    return new Promise((resolve, reject) => {
      this.socket.onopen = () => {
        console.log("WebSocket connection opened");
        // Reset the reconnection interval on successful connection.
        this.reconnectInterval = 5000;
        resolve();
      };

      this.socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        // Error handling: onclose will take care of reconnect logic.
      };

      // Combined onclose handler that manages custom callback and reconnection.
      this.socket.onclose = (event) => {
        console.log("WebSocket connection closed:", event);
        
        // Call the custom onClose callback if it has been set.
        if (typeof this.customOnClose === 'function') {
          this.customOnClose(event);
        }
        
        if (!this.forcedClose) {
          // Attempt to reconnect after the current interval.
          this.timeoutId = setTimeout(() => {
            // Increase the interval with an exponential backoff strategy.
            this.reconnectInterval = Math.min(
              this.reconnectInterval * this.reconnectDecay,
              this.maxReconnectInterval
            );
            console.log(`Reconnecting in ${this.reconnectInterval} ms...`);
            this.connect();
          }, this.reconnectInterval);
        }
      };
    });
  }

  // Allows external code to register a custom onClose callback.
  onClose(callback) {
    if (typeof callback === 'function') {
      this.customOnClose = callback;
    } else {
      console.error("Provided onClose callback is not a function.");
    }
  }

  onMessage(callback) {
    if (this.socket) {
      this.socket.onmessage = (event) => {
        callback(event.data);
      };
    }
  }

  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(message);
    } else {
      console.error("WebSocket is not open. Cannot send message.");
    }
  }

  disconnect() {
    // Prevent the reconnection logic from re-triggering.
    this.forcedClose = true;
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
    if (this.socket) {
      this.socket.close();
      console.log("WebSocket connection closed");
    }
  }
}

export default WebSocketService;
