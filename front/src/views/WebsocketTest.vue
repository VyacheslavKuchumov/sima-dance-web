<template>
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8">
          <v-card>
            <v-card-title class="headline">Vue WebSocket Test</v-card-title>
            <v-card-text>
              <v-text-field
                v-model="message"
                label="Enter a message"
                outlined
              ></v-text-field>
              <v-btn color="primary" @click="sendMessage">Send Message</v-btn>
              <div v-if="messages.length" class="mt-3">
                <v-alert
                  v-for="(msg, index) in messages"
                  :key="index"
                  type="info"
                  dense
                  text
                  class="mb-2"
                >
                  <strong>Received:</strong> {{ msg }}
                </v-alert>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  import WebSocketService from '@/websocket/WebSocketService.js';
  
  export default {
    name: "WebsocketTest",
    data() {
      return {
        message: "",
        messages: [],
        wsService: null,
      };
    },
    async created() {
      // Initialize the WebSocket service with your backend URL
      this.wsService = new WebSocketService();
      try {
        await this.wsService.connect();
        // Listen for incoming messages
        this.wsService.onMessage((data) => {
          console.log("Message received:", data);
          this.messages.push(data);
        });
        // Optionally, handle the close event
        this.wsService.onClose((event) => {
          console.log("WebSocket closed:", event);
        });
      } catch (error) {
        console.error("Failed to connect:", error);
      }
    },
    beforeDestroy() {
      // Gracefully close the WebSocket connection when the component is destroyed
      if (this.wsService && typeof this.wsService.disconnect === 'function') {
        this.wsService.disconnect();
      }
    },
    beforeRouteLeave(to, from, next) {
      if (this.wsService && typeof this.wsService.disconnect === 'function') {
        this.wsService.disconnect();
      }
      next();
    },
    methods: {
      sendMessage() {
        // Send the user's message through the WebSocket and clear the input
        if (this.message.trim() !== "") {
          this.wsService.send(this.message);
          this.message = "";
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .mt-3 {
    margin-top: 1rem;
  }
  .mb-2 {
    margin-bottom: 0.5rem;
  }
  </style>
  