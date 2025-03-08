import { createStore } from "vuex";
import auth from "@/store/auth";
import user from "@/store/user";
import events from "@/store/events";
import seats from "@/store/seats";



export default createStore({
  state: {},
  getters: {},
  mutations: {},
  actions: {},
  modules: {
    auth: auth,
    user: user,
    events: events,
    seats: seats,

  },
});
