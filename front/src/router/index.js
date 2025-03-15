import { createRouter, createWebHistory } from "vue-router";
import instance from "@/middlewares";

import HomeView from "@/views/HomeView.vue";
import Register from "@/views/Auth/Register.vue";
import Login from "@/views/Auth/Login.vue";
import ArchivedEventsAdminView from "@/views/Admin/ArchivedEventsAdminView.vue";
import EventsAdminView from "@/views/Admin/EventsAdminView.vue";
import EventsView from "@/views/User/EventsView.vue";
import AdminSeatsInEventView from "@/views/Admin/AdminSeatsInEventView.vue";
import SeatsBookingView from "@/views/User/SeatsBookingView.vue";
import AdminBookingsView from "@/views/Admin/AdminBookingsView.vue";
const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: { auth: true },
  },
  {
    path: "/register",
    name: "register",
    component: Register,
  },
  {
    path: "/login",
    name: "login",
    component: Login,
  },
  {
    path: "/admin/events",
    name: "events-admin",
    component: EventsAdminView,
    // meta: { auth: true, admin: true },
  },
  {
    path: "/admin/archived-events",
    name: "archived-events-admin",
    component: ArchivedEventsAdminView,
    // meta: { auth: true, admin: true },
  },
  {
    path: "/admin/event/:uid",
    name: "seats-admin",
    component: AdminSeatsInEventView,
    // meta: { auth: true, admin: true },
    props: true,
  },
  {
    path: "/admin/bookings/:event_uid",
    name: "bookings-admin",
    component: AdminBookingsView,
    // meta: { auth: true, admin: true },
    props: true,
  },
  {
    path: "/events",
    name: "events",
    component: EventsView,
    meta: { auth: true },
  },
  {
    path: "/event/:uid",
    name: "booking-seats",
    component: SeatsBookingView,
    meta: { auth: true },
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from, next) => {
  try {
    const requireAuth = to.matched.some(record => record.meta.auth);
    if (requireAuth) {
      const uid = localStorage.getItem("uid");
      const response = await instance.get(`/api/users/${uid}`);
      if (response.status === 200) {
        // Check if the route requires admin access
        if (to.matched.some(record => record.meta.admin)) {
          // Assuming the response data has a 'role' property
          if (response.data.role !== 'admin') {
            // Redirect non-admin users to the home page
            return next("/");
          }
        }
        return next();
      } else if (response.status === 403) {
        return next("/login");
      }
    }
    return next();
  } catch (error) {
    return next("/login");
  }
});

export default router;
