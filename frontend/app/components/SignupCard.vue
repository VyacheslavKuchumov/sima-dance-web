
<template>
    <UCard class="w-full max-w-md">
      <template #header>
        <h2 class="text-xl font-semibold">Регистрация</h2>
      </template>

      <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
        <UFormField label="Логин" name="username" required>
          <UInput
            class="w-full"
            v-model="state.username"
            placeholder="Придумайте логин"
            :disabled="loading"
          />
        </UFormField>

        <UFormField label="Пароль" name="password" required>
          <UInput
            class="w-full"
            v-model="state.password"
            type="password"
            placeholder="Придумайте пароль"
            :disabled="loading"
          />
        </UFormField>

        <UFormField label="Подтверждение пароля" name="confirmPassword" required>
          <UInput
            class="w-full"
            v-model="state.confirmPassword"
            type="password"
            placeholder="Подтвердите пароль"
            :disabled="loading"
          />
        </UFormField>

        <UButton
          type="submit"
          color="primary"
          block
          :loading="loading"
          :disabled="!v.safeParse(schema, state).success"
        >
          Регистрация
        </UButton>
      </UForm>

      <template #footer>
        <div class="text-center">
          Уже есть аккаунт?
          <NuxtLink to="/login" class="text-primary underline ml-1">
            Войти в аккаунт
          </NuxtLink>
        </div>
      </template>
    </UCard>

</template>

<script setup lang="ts">

import * as v from 'valibot'
import type { FormSubmitEvent } from '@nuxt/ui'


// const username  = ref('')
// const password  = ref('')
const loading   = ref(false)

const auth   = useAuthStore()
const router = useRouter()

  
const schema = v.pipe(
  v.object({
    username: v.pipe(
      v.string(),
      v.minLength(2, 'Имя пользователя должно содержать минимум 2 символа')
    ),
    password: v.pipe(
      v.string(),
      v.minLength(8, 'Пароль должен содержать минимум 8 символов')
    ),
    confirmPassword: v.pipe(
      v.string(),
    )
  }),
  v.forward(
    v.partialCheck(
      [['password'], ['confirmPassword']],
      (input) => input.password === input.confirmPassword,
      'Пароли не совпадают'
    ),
    ['confirmPassword']
  )
)

type Schema = v.InferOutput<typeof schema>

const state = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const toast = useToast()
async function onSubmit(event: FormSubmitEvent<Schema>) {

  loading.value = true
  try {
    await auth.signup({
      username:  event.data.username,
      password:  event.data.password,
    })
    toast.add({ title: 'Успешно', description: 'Вы были зарегистрированы.', color: 'success' })
    router.push('/')
  } catch (err) {
    console.error(err)
    if (err instanceof Error) {
      toast.add({ title: 'Ошибка', description: err.message, color: 'error' })
    } else {
      toast.add({ title: 'Ошибка', description: 'Произошла непредвиденная ошибка', color: 'error' })
    }
  } finally {
    loading.value = false
  }
}
</script>
