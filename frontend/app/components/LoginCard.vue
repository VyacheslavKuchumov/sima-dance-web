<template>
  <UCard class="w-full max-w-md">
    <template #header>
      <h2 class="text-xl font-semibold">Войти в аккаунт</h2>
    </template>

    <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
      <UFormField label="Логин" name="username" required>
        <UInput
          class="w-full"
          v-model="state.username"
          placeholder="Введите имя пользователя"
          :disabled="loading"
        />
      </UFormField>

      <UFormField label="Пароль" name="password" required>
        <UInput
          class="w-full"
          v-model="state.password"
          type="password"
          placeholder="Введите пароль"
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
        Войти в аккаунт
      </UButton>
    </UForm>

    <template #footer>
      <div class="text-center">
        Нет аккаунта?
        <NuxtLink to="/signup" class="text-primary underline ml-1">
          Зарегистрироваться
        </NuxtLink>
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
import * as v from 'valibot'
import type { FormSubmitEvent } from '@nuxt/ui'

const loading = ref(false)
const auth    = useAuthStore()
const router  = useRouter()
const toast   = useToast()

// Schema
const schema = v.object({
  username: v.pipe(
    v.string(),
  ),
  password: v.pipe(
    v.string(),
  )
})

type Schema = v.InferOutput<typeof schema>

// State
const state = reactive({
  username: '',
  password: ''
})

async function onSubmit(event: FormSubmitEvent<Schema>) {
  loading.value = true
  try {
    await auth.login({
      username: event.data.username,
      password: event.data.password,
    })
    toast.add({ title: 'Успешно', description: 'Вы вошли в аккаунт', color: 'success' })
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