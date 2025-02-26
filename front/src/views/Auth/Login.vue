<template>
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
      go_login() {
        if (this.$refs.loginForm.validate()) {
          const formData = {
            email: this.email,
            password: this.password,
          };
          this.login(formData);
        }
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
  