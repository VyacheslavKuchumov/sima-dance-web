import instance from "@/middlewares";

export default {
  name: "seats_in_events",
  state: () => ({
    data: null,
  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },
  },
  actions: {
    // Get all seats in events
    async getSeatsInEvents({ commit }) {
      try {
        const response = await instance.get("/api/seats_in_events");
        if (response) {
          commit("setData", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error fetching seats in events:", error);
      }
    },

    // Create a new seat in an event
    async createSeatInEvent({}, seatInEvent) {
      try {
        const response = await instance.post("/api/seats_in_events", {
          seat_id: seatInEvent.seat_id,
          event_uid: seatInEvent.event_uid,
          status: seatInEvent.status, // Default is "available" if not provided
          price: seatInEvent.price,
        });
        if (response) {
          console.log("Seat in event created:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error creating seat in event:", error);
      }
    },

    // Update an existing seat in an event by id
    async updateSeatInEvent({}, { id, seatInEvent }) {
      try {
        const response = await instance.put(`/api/seats_in_events/${id}`, {
          seat_id: seatInEvent.seat_id,
          event_uid: seatInEvent.event_uid,
          status: seatInEvent.status,
          price: seatInEvent.price,
        });
        if (response) {
          console.log("Seat in event updated:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error updating seat in event:", error);
      }
    },

    // Delete an existing seat in an event by id
    async deleteSeatInEvent({}, id) {
      try {
        const response = await instance.delete(`/api/seats_in_events/${id}`);
        if (response) {
          console.log("Seat in event deleted:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error deleting seat in event:", error);
      }
    },
  },
  namespaced: true,
};
