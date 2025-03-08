import instance from "@/middlewares";

export default {
  name: "venues",
  state: () => ({
    data: null,
  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },
  },
  actions: {
    // Get all venues
    async getVenues({ commit }) {
      try {
        const response = await instance.get("/api/venues");
        if (response) {
          commit("setData", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error fetching venues:", error);
      }
    },

    // Create a new venue
    async createVenue({}, venue) {
      try {
        const response = await instance.post("/api/venues", {
          venue_name: venue.venue_name,
        });
        if (response) {
          console.log("Venue created:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error creating venue:", error);
      }
    },

    // Update an existing venue by id
    async updateVenue({}, { id, venue }) {
      try {
        const response = await instance.put(`/api/venues/${id}`, {
          venue_name: venue.venue_name,
        });
        if (response) {
          console.log("Venue updated:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error updating venue:", error);
      }
    },

    // Delete an existing venue by id
    async deleteVenue({}, id) {
      try {
        const response = await instance.delete(`/api/venues/${id}`);
        if (response) {
          console.log("Venue deleted:", response.data);
          return response.data;
        }
      } catch (error) {
        console.error("Error deleting venue:", error);
      }
    },
  },
  namespaced: true,
};
