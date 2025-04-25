import instance from "@/middlewares";

export default {
  name: "bookings",
  state: () => ({
    data: null,
  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },
  },
  actions: {
    // // Get all bookings
    // async getBookings({ commit }) {
    //   try {
    //     const response = await instance.get("/api/bookings");
    //     if (response) return commit("setData", response.data);
    //   } catch (error) {
    //     console.error(error);
    //   }
    // },

    // Get bookings by event_uid
    async getBookingsByEventUid({ commit }, event_uid) {
      try {
        const response = await instance.get(`/api/bookings/event/${event_uid}`);
        if (response) return commit("setData", response.data);
      } catch (error) {
        console.error(error);
      }
    },
    
    // Toggle booking status
    async togglePaidStatus({}, booking_id) {
      try {
        const response = await instance.put(`/api/bookings/payment/${booking_id}`);
        if (response) return  response.data;
      } catch (error) {
        console.error(error);
      }
    },

    // Create a new booking
    async createBooking({}, booking) {
      try {
        const response = await instance.post("/api/bookings", {
          user_uid: booking.user_uid,
          seat_in_event_id: booking.seat_in_event_id,
        });
        if (response) {
          console.log("Booking created:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error(error);
      }
    },

    // Confirm a booking
    async confirmBooking({}, booking_id) {
      try {
        const uid = localStorage.getItem("uid");
        const response = await instance.put(`/api/bookings/confirm/${booking_id}/${uid}`);
        if (response) {
          console.log("Booking confirmed:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error(error);
      }
    },

    // toggle ticket status
    async toggleTicketStatus({}, booking_id) {
      try {
        const response = await instance.put(`/api/bookings/ticket/${booking_id}`);
        if (response) {
          console.log("Booking status toggled:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error(error);
      }
    },

    // Update an existing booking by id
    async updateBooking({}, { id, booking }) {
      try {
        const response = await instance.put(`/api/bookings/${id}`, {
          user_uid: booking.user_uid,
          seat_in_event_id: booking.seat_in_event_id,
          booking_date: booking.booking_date,
          confirmed: booking.confirmed,
          paid: booking.paid,
        });
        if (response) {
          console.log("Booking updated:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error(error);
      }
    },

    // Delete an existing booking by id
    async deleteBooking({}, id) {
      try {
        const uid = localStorage.getItem("uid");
        const response = await instance.delete(`/api/bookings/${id}/${uid}`);
        if (response) {
          console.log("Booking deleted:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error(error);
      }
    },
  },
  namespaced: true,
};
