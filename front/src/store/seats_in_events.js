import instance from "@/middlewares";

export default {
  name: "seats_in_events",
  state: () => ({
    data: null,
    seat_in_event: null,
  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },
    setSeatInEvent(state, seat_in_event) {
      state.seat_in_event = seat_in_event;
    },
    updateSeatsInEventStatus(state, payload) {
      const { seat_in_event_id, status } = payload;
      const seat = state.data.find(
        item => item.seat_in_event_id === seat_in_event_id
      );
      if (seat) {
        seat.status = status;
      }
    },
  },
  actions: {
    async updateSeatInStore({ commit }, payload) {
      console.log("updateSeatInStore", payload);
      commit("updateSeatsInEventStatus", payload);
    },

    // Initialize seats in event by venue_id and event_uid
    async initSeatsInEvent({ commit }, { venue_id, event_uid }) {
      try {
        const response = await instance.post(`/api/seats_in_events/initialize/${venue_id}/${event_uid}`);
        if (response) {
          commit("setData", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error initializing seats in event:", error);
      }
    },

    // get seats in event by id
    async getSeatInEventById({ commit }, id) {
      try {
        const response = await instance.get(`/api/seats_in_events/id/${id}`);
        if (response) {
          commit("setSeatInEvent", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error fetching seat in event by ID:", error);
      }
    },

    // Get all seats in events
    async getSeatsInEvent({ commit }, uid) {
      try {
        const response = await instance.get(`/api/seats_in_events/${uid}`);
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
    async updateSeatInEvent({}, {id, status, price}) {
      try {
        const response = await instance.put(`/api/seats_in_events/${id}`, {
          
          status: status,
          price: price,
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
