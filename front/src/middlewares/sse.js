// Create a function to handle SSE connections

export function SSEConnection() {
    const url = process.env.VUE_APP_SERVER + "/api/sse/updates";
    const eventSource = new EventSource(url);

    // Return the eventSource for potential future cleanup or interaction
    return eventSource;
  }
