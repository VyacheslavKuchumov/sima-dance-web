import instance from "@/middlewares";
import { SSEConnection } from "@/middlewares/sse";


export default {
  name: "sse",
  state: () => ({
    data: null,
  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },
  },
  actions: {
    async startListeningToBookingUpdates({ commit, dispatch }) {
        const eventSource = SSEConnection();
        eventSource.onmessage = function(event) {
          try {
            console.log(event);
            const stream = JSON.parse(event.data);
            console.log(stream);
            commit("setData", stream.data);
            dispatch("seats_in_events/updateSeatInStore", 
                {
                seat_in_event_id: stream.data.seat_in_event_id,
                status: stream.data.status
                },
                { root: true });
          } catch (error) {
            console.error("Error processing SSE data:", error);
          }
        }
      },
  },

  namespaced: true,
};
