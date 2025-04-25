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
              
              <v-card-title class="text-wrap"> <v-icon>mdi-account</v-icon> <strong> {{ user().name }}</strong> </v-card-title>
              <!-- Event Details -->
              <v-card-text>
                <p>ФИО ребенка: <strong>{{ user().child_name }}</strong> </p>
                <p>Группа: <strong>{{ user().group_name }}</strong> </p>
              </v-card-text>
  
              <!-- Action Buttons -->
              <v-card-actions class="justify-center">
                <v-btn color="primary" @click="openDialog">Редактировать</v-btn>

              </v-card-actions>
        </v-card>
      </v-container>
    </v-card>
    <!-- Editing Dialog -->
    <v-dialog v-model="dialog" max-width="500">
      <v-card>
        <v-card-title>
          <span class="headline">Редактировать</span>
        </v-card-title>
        <v-card-text>
          <v-text-field
            label="ФИО родителя"
            v-model="userName"
          ></v-text-field>
          <v-text-field
            label="ФИО ребенка"
            v-model="childName"
          ></v-text-field>
          <v-select label="Выберите группу ребенка"
          v-model="group_name"
          :items="['Беби 1', 
                  'Беби 2', 
                  'Средние 1',
                  'Средние 2',
                  'Средние 3',
                  'Старшие 1',
                  'Старшие 2',
                  'Старшие 3',
                  'Cтаршие 11',
                  'Сборные']"></v-select>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="red" text @click="closeDialog">Отменить</v-btn>
          <v-btn color="primary" text @click="saveChanges">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
  </template>
  
  <script>
  import { mapActions, mapState } from "vuex";
  
  
  export default {
    name: "HomeView",
    data() {
      return {
        overlay: false,
        hasUserInfo: false,
        dialog: false,
        userName: "",
        childName: "",
        group_name: "",
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
        // Open dialog and pre-fill with current user data from the store
      openDialog() {
        // Assuming your Vuex store's module is named "user" and state.user contains the user details
        if (this.$store.state.user.user) {
          this.userName = this.$store.state.user.user.name || '';
          this.childName = this.$store.state.user.user.child_name || '';
          this.group_name = this.$store.state.user.user.group_name || '';
        }
        this.dialog = true;
      },
      // Close the dialog
      closeDialog() {
        this.dialog = false;
      },
      // Dispatch the updateUser action to update the user details in the store
      async saveChanges() {
        try {
          await this.$store.dispatch('user/updateUser', {
            name: this.userName,
            child_name: this.childName,
            group_name: this.group_name,
          });
          this.closeDialog();
        } catch (error) {
          console.error('Error updating user:', error);
        }
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