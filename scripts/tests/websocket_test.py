import time
from locust import User, task, between
from websocket import create_connection, WebSocketConnectionClosedException

class WebSocketUser(User):
    wait_time = between(1, 3)  # Simulates user think time between tasks

    def on_start(self):
        # Establish a WebSocket connection upon user start.
        try:
            self.ws = create_connection("ws://your-websocket-server-url")
            print("WebSocket connection established.")
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.ws = None

    def on_stop(self):
        # Ensure the connection is gracefully closed when the user stops.
        if self.ws:
            self.ws.close()
            print("WebSocket connection closed.")

    @task
    def receive_messages(self):
        # Task dedicated to only receiving messages from the server.
        if not self.ws:
            print("No active connection. Attempting to reconnect.")
            self.on_start()
            return

        try:
            # Waiting to receive a message from the WebSocket server.
            response = self.ws.recv()
            print(f"Received message: {response}")
        except WebSocketConnectionClosedException:
            print("WebSocket connection closed unexpectedly. Reconnecting.")
            self.on_start()
        except Exception as e:
            print(f"An error occurred: {e}")

        # Optional pause to simulate user think time.
        time.sleep(1)
