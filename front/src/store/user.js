import instance from "@/middlewares";

export default {
  name: "user",
  state: () => ({
    user: null,
    userNames: [],
  }),
  mutations: {
    setUser(state, user) {
      state.user = user;
    },
    setUserNames(state, names) {
      state.userNames = names;
    },
  },
  actions: {

    async getUserByUid({ commit }) {
      const uid = localStorage.getItem("uid");
      const user = await instance.get(`/api/users/${uid}`);
      if (user) {
        console.log(user.data);
        localStorage.setItem("username", user.data.name);
      }
      if (user) return commit("setUser", user.data);

      console.log(user.message);
    },

    async updateUser({ commit }, { name, child_name }) {
      const uid = localStorage.getItem("uid");
      const response = await instance.put(`/api/users/${uid}`, {
        name: name,
        child_name: child_name,
      });
      if (response) {
        console.log(response.data);
        return commit("setUser", response.data);
      }
    }

  },

  namespaced: true,
};
