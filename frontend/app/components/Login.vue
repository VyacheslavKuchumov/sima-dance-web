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