<template>
  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate></v-progress-circular>
  </v-overlay>
    <v-container>
        <v-card-title>Войти</v-card-title>
        <v-form @submit.prevent="onSubmit" ref="loginForm" v-model="valid" lazy-validation>
            <v-text-field
              label="Введите логин"
              v-model="login"
              :rules="loginRules"
              required
              type="text"
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
            
            <v-btn class="mt-5" variant="plain" text to="/signup">Нет аккаунта?</v-btn>
            
        </v-form>
    </v-container>
    <ErrorDialog v-if="dialog" :message="error" />
</template>

<script setup>

const overlay = ref(false)
const loginForm = ref(null)
const login = ref('')
const password = ref('')
const valid = ref(false)


const router  = useRouter()
const auth = useAuthStore()

const error = ref('')
const dialog = ref(false)


const loginRules = ref([
  v => !!v || 'Логин обязателен',
  v => (v && v.length >= 3) || 'Логин должен быть не менее 3 символов',
])

const passwordRules = ref([(v) => !!v || "Пароль обязателен"])


async function onSubmit() {
  overlay.value = true
  try {
    await auth.login({
      username: login.value,
      password: password.value,
    })
    router.push('/')
    
  } catch (err) {
    console.error(err)
    error.value = err.message
    dialog.value = true

  } finally {
    overlay.value = false
  }
}


</script>