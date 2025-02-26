import instance from "@/middlewares";


export default {
  name: "professions",
  state: () => ({
    data: null,

  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },

  },
  actions: {
    // get professions
    async getProfessions({ commit }) {
        try {
            const response = await instance.get("/api/professions");
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },

    // create profession
    async createProfession({}, input) {
        try {
            const { profession_name } = input;
            const response = await instance.post("/api/professions", { profession_name });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },
    
    // update profession
    async updateProfession({}, input) {
        try {
            const { profession_id, profession_name } = input;
            const response = await instance.put("/api/professions", { profession_id, profession_name });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },
    
    // delete profession
    async deleteProfession({}, profession_id) {
        try {
            const response = await instance.delete(`/api/professions/${profession_id}`);
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },
    
  },

  namespaced: true,
};
