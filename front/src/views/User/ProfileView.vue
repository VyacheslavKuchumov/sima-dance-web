<template>
    <v-overlay
        :model-value="overlay"
        class="align-center justify-center"
      >
        <v-progress-circular
          color="primary"
          size="64"
          indeterminate
        ></v-progress-circular>
      </v-overlay>
    <!-- Header Card -->
    <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
      <v-card-title class="text-wrap" align="center">
        Личный кабинет
      </v-card-title>
    </v-card>
    <!-- Main Card with Toolbar and Cards for each Event -->
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
        <v-spacer></v-spacer>
        <!-- <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn> -->
      </v-toolbar>
      <v-container>
        <v-card class="ma-2" >
              
              <v-card-title class="text-wrap"> <v-icon>mdi-account</v-icon> <strong> Пользователь: {{ user().name }}</strong> </v-card-title>
              <!-- Event Details -->
              <v-card-text>
                Lorem ipsum dolor sit amet
              </v-card-text>
  
              <!-- Action Buttons -->
              <v-card-actions class="justify-center">
                <v-btn color="primary" @click="">Редактировать</v-btn>

              </v-card-actions>
            </v-card>
      </v-container>
    </v-card>
    
  </template>
  
  <script>
  import { mapActions, mapState } from "vuex";
  
  
  export default {
    name: "HomeView",
    data() {
      return {
        overlay: false,
        hasUserInfo: false,
  
      };
    },
    computed: {},
    methods: {
      ...mapActions({
        getUser: "user/getUserByUid",
      }),

      user() {
        return this.$store.state.user.user || {};
      },
      goBack() {
        this.$router.go(-1);
      },
    },
    watch: {},
  
    
    async mounted() {
      this.overlay = true;
      
      this.uid = localStorage.getItem("uid");
  
      if (this.uid) {
  
        await this.getUser();
  
      }
      this.overlay = false;
    },
  };
  </script>