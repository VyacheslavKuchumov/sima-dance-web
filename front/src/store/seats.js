import instance from "@/middlewares";

export default {
  name: "seats",
  state: () => ({
    data: null,
  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },
  },
  actions: {

    // # function for getting all seats
    async getSeats({ commit }) {
      try {
        const response = await instance.get("/api/seats");
        if (response) return commit("setData", response.data);
      } catch (error) {
        console.log(error);
      }
    },

    // # function for creating a new seat
    async createSeat({}, seat) {
      try {
        const response = await instance.post("/api/seats", {
          section: seat.section,
          row: seat.row,
          number: seat.number,
          venue_id: seat.venue_id,
        });
        if (response) {
          console.log("Seat created:", response.data);
          return response.data;
        }
      } catch (error) {
        console.log(error);
      }
    },

    // # function for updating an existing seat by id
    async updateSeat({}, { id, seat }) {
      try {
        const response = await instance.put(`/api/seats/${id}`, {
          section: seat.section,
          row: seat.row,
          number: seat.number,
          venue_id: seat.venue_id,
        });
        if (response) {
          console.log("Seat updated:", response.data);
          return response.data;
        }
      } catch (error) {
        console.log(error);
      }
    },

    // # function for deleting an existing seat by id
    async deleteSeat({}, id) {
      try {
        const response = await instance.delete(`/api/seats/${id}`);
        if (response) {
          console.log("Seat deleted:", response.data);
          return response.data;
        }
      } catch (error) {
        console.log(error);
      }
    },
  },

  namespaced: true,
};
