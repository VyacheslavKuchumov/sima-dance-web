import { createRouter, createWebHistory } from "vue-router";
import instance from "@/middlewares";


import HomeView from "@/views/HomeView.vue";
import Register from "@/views/Auth/Register.vue";
import Login from "@/views/Auth/Login.vue";

import OkvedView from "@/views/okved/1OkvedSectionsView.vue";
import OkvedClassesView from "@/views/okved/2OkvedClassesView.vue";
import OkvedSubclassesView from "@/views/okved/3OkvedSubclassesView.vue";
import OkvedGroupsView from "@/views/okved/4OkvedGroupsView.vue";
import OkvedSubgroupsView from "@/views/okved/5OkvedSubgroupsView.vue";
import OkvedActivitiesView from "@/views/okved/6OkvedActivitiesView.vue";
import EmploymentMinstatView from "@/views/Minstat/EmploymentMinstatView.vue";

import ProfessionsView from "@/views/ProfessionsView.vue";

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
    path: "/okved",
    name: "okved",
    component: OkvedView,
    meta: { auth: true },
  },
  {
    path: "/employment_minstat",
    name: "employment_minstat",
    component: EmploymentMinstatView,
    meta: { auth: true },
  },
  {
    path: "/okved/class/:id",
    name: "okved-classes",
    component: OkvedClassesView,
    meta: { auth: true },
  },
  {
    path: "/okved/subclass/:id",
    name: "okved-subclasses",
    component: OkvedSubclassesView,
    meta: { auth: true },
  },
  {
    path: "/okved/group/:id",
    name: "okved-groups",
    component: OkvedGroupsView,
    meta: { auth: true },
  },
  {
    path: "/okved/subgroup/:id",
    name: "okved-subgroups",
    component: OkvedSubgroupsView,
    meta: { auth: true },
  },
  {
    path: "/okved/activity/:id",
    name: "okved-activities",
    component: OkvedActivitiesView,
    meta: { auth: true },
  },
  {
    path: "/professions",
    name: "professions",
    component: ProfessionsView,
    
  },
  
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from, next) => {
  try {
    const requireAuth = to.matched.some((record) => record?.meta.auth);
    if (requireAuth) {
      const uid = localStorage.getItem("uid");
      const response = await instance.get(`/api/users/${uid}`);
      if (response.status == 200) {
        return next();
      } else if (response.status == 403) {
        return next("/login");
      }
    }
    return next();
  } catch (error) {
    return next("/login");
  }
});

export default router;
