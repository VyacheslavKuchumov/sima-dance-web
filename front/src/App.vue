<template>
  <v-app>
    
    <v-app-bar color="primary">
      <v-toolbar-title @click="this.$router.push(`/`);">SimaDancing</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-app-bar-nav-icon v-if="isAuth" @click="drawer = !drawer" />
    </v-app-bar>
    <v-navigation-drawer
      v-model="drawer"
      location="right"
      app
      temporary
    >
      <v-list>
        
          <v-list-item v-if="isAuth" to="/">
            <v-list-item-title>Главная</v-list-item-title>
          </v-list-item>
<!-- 
          <v-list-item v-if="isAuth" to="/events">
            <v-list-item-title>Концерты</v-list-item-title>
          </v-list-item> -->

          <v-list-item v-if="isAuth" to="/profile">
            <v-list-item-title>Личный кабинет</v-list-item-title>
          </v-list-item>
          
          <v-list-item v-if="isAuth && isAdmin" to="/admin/events">
            <v-list-item-title>Управление концертами</v-list-item-title>
          </v-list-item>

          <v-list-item v-if="isAuth && isAdmin" to="/admin/archived-events">
            <v-list-item-title>Архив концертов</v-list-item-title>
          </v-list-item>

          
         
          <v-list-item v-if="isAuth" @click="logout()">
            <v-list-item-title>Выйти</v-list-item-title>
          </v-list-item>
        
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { mapActions, mapState } from "vuex";
export default {
  data() {
    return {
      drawer: false, // State for navigation drawer
    };
  },
  
  methods: {
    ...mapActions({
      logout: "auth/logout",
    }),
  },
  mounted() {
    const uid = localStorage.getItem("uid");
    uid
      ? this.$store.commit("auth/setAuth", true)
      : this.$store.commit("auth/setAuth", false);
  },

  computed: {
    ...mapState({
      isAuth: (state) => state.auth.isAuth,
      isAdmin: (state) => state.auth.isAdmin,
    }),

  },
};
</script>


