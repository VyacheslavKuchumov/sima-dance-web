import { createStore } from "vuex";
import auth from "@/store/auth";
import user from "@/store/user";
import events from "@/store/events";
import seats from "@/store/seats";
import bookings from "@/store/bookings";
import seats_in_events from "@/store/seats_in_events";
import venues from "@/store/venues";



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
    bookings: bookings,
    seats_in_events: seats_in_events,
    venues: venues,
  },
});
