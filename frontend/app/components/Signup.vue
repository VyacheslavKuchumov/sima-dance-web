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
            placeholder="Иванов Иван Иванович"
            required
            type="text"
            ></v-text-field>
            <v-text-field
            label="Введите ФИО ребенка"
            v-model="child_name"
            :rules="nameRules"
            placeholder="Иванов Иван Иванович"
            required
            type="text"
            ></v-text-field>
            <v-select
            label="Выберите группу ребенка"
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
                    'Сборные']"

            :rules="groupRules"
            required
            ></v-select>

            <v-btn type="submit" :disabled="!valid" class="form-btn" color="primary">
            Регистрация
            </v-btn>
            
            
            <v-btn class="mt-5" variant="plain" text to="/login">Уже есть аккаунт?</v-btn>
            
        </v-form>
    </v-container>
  </template>