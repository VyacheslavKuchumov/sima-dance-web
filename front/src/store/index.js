import { createStore } from "vuex";
import auth from "@/store/auth";
import user from "@/store/user";
import okved from "@/store/okved";
import professions from "@/store/professions";
import employment_minstat from "@/store/employment_minstat";



export default createStore({
  state: {},
  getters: {},
  mutations: {},
  actions: {},
  modules: {
    auth: auth,
    user: user,
    okved: okved,
    professions: professions,
    employment_minstat: employment_minstat,
  },
});
