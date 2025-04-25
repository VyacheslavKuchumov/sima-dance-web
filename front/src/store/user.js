import instance from "@/middlewares";

export default {
  name: "user",
  state: () => ({
    user: null,
    users: null,
  }),
  mutations: {
    setUser(state, user) {
      state.user = user;
    },
    setUsers(state, users) {
      state.users = users;
    }
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

    async updateUser({ commit }, input) {
      const { name, child_name, group_name } = input;
      const uid = localStorage.getItem("uid");
      const response = await instance.put(`/api/users/${uid}`, {
        name: name,
        child_name: child_name,
        group_name: group_name,
      });
      if (response) {
        console.log(response.data);
        return commit("setUser", response.data);
      }
    },

    // get all users
    async getAllUsers({ commit }) {
      const response = await instance.get("/api/users");
      if (response) {
        console.log(response.data);
        return commit("setUsers", response.data);
      }
    },

  },

  namespaced: true,
};
