<template>
  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate></v-progress-circular>
  </v-overlay>
    <v-container class="home" fluid>
        <v-card-title>Войти</v-card-title>
        <v-form @submit.prevent="go_login" ref="loginForm" v-model="valid" lazy-validation>
            <v-text-field
            label="Введите email"
            v-model="email"
            :rules="emailRules"
            required
            type="email"
            ></v-text-field>
            <v-text-field
            label="Введите пароль"
            v-model="password"
            :rules="passwordRules"
            required
            type="password"
            ></v-text-field>
            <v-btn type="submit" :disabled="!valid" class="form-btn" color="primary">
            Войти
            </v-btn>
            
            <v-btn class="mt-5" variant="plain" text to="/register">Нет аккаунта?</v-btn>
            
        </v-form>
    </v-container>
  </template>
  
  <script>
  import { mapActions } from "vuex";
  
  export default {
    name: "login",
    data() {
      return {
        overlay: false,
        email: "",
        password: "",
        valid: false,
        emailRules: [(v) => !!v || "Email обязателен", (v) => /.+@.+\..+/.test(v) || "Email должен быть действительным"],
        passwordRules: [(v) => !!v || "Пароль обязателен"],
      };
    },
    methods: {
      ...mapActions({
        login: "auth/login",
      }),
      async go_login() {
        this.overlay = true;
        if (this.$refs.loginForm.validate()) {
          const formData = {
            email: this.email,
            password: this.password,
          };
          await this.login(formData);
        }
        this.overlay = false;
      },
    },
  };
  </script>
  
  <style>
  .home {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }
  .v-form {
    max-width: 400px;
    width: 100%;
  }
  .form-btn {
    width: 100%;
  }
  </style>
  