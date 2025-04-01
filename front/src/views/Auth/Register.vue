<template>
  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate></v-progress-circular>
  </v-overlay>
    <v-container class="home" fluid>
        <v-card-title>Зарегистрироваться</v-card-title>
        <v-form @submit.prevent="go_register" ref="registerForm" v-model="valid" lazy-validation>
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
            <v-text-field
            label="Введите ФИО родителя"
            v-model="name"
            :rules="nameRules"
            placeholder="Иванов И. И."
            required
            type="text"
            ></v-text-field>
            <v-text-field
            label="Введите ФИО ребенка"
            v-model="child_name"
            :rules="nameRules"
            placeholder="Иванов И. И."
            required
            type="text"
            ></v-text-field>
            <v-btn type="submit" :disabled="!valid" class="form-btn" color="primary">
            Регистрация
            </v-btn>
            
            
            <v-btn class="mt-5" variant="plain" text to="/login">Уже есть аккаунт?</v-btn>
            
        </v-form>
    </v-container>
  </template>
  
  <script>
  import { mapActions } from "vuex";
  
  export default {
    name: "register",
    data() {
      return {
        overlay: false,
        email: "",
        password: "",
        name: "",
        child_name: "",
        valid: false,
        emailRules: [(v) => !!v || "Email обязателен", (v) => /.+@.+\..+/.test(v) || "Email должен быть действительным"],
        passwordRules: [(v) => !!v || "Пароль обязателен"],
        nameRules: [(v) => !!v || "Имя обязательно"],
      };
    },
    methods: {
      ...mapActions({
        register: "auth/register",
      }),
      async go_register() {
        this.overlay = true;
        if (this.$refs.registerForm.validate()) {
          const formData = {
            email: this.email,
            password: this.password,
            name: this.name,
            child_name: this.child_name,
          };
          await this.register(formData);
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
  