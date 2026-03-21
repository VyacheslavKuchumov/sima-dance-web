<template>
  <UCard class="w-full">
    <template #header>
      <div class="space-y-1">
        <h2 class="text-xl font-semibold">Смена пароля</h2>
        <p class="text-sm text-muted">
          Для безопасности укажите текущий пароль и задайте новый.
        </p>
      </div>
    </template>

    <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
      <UFormField label="Текущий пароль" name="currentPassword" required>
        <UInput
          v-model="state.currentPassword"
          class="w-full"
          type="password"
          placeholder="Введите текущий пароль"
          :disabled="loading"
        />
      </UFormField>

      <UFormField label="Новый пароль" name="newPassword" required>
        <UInput
          v-model="state.newPassword"
          class="w-full"
          type="password"
          placeholder="Минимум 8 символов"
          :disabled="loading"
        />
      </UFormField>

      <UFormField label="Подтверждение пароля" name="confirmPassword" required>
        <UInput
          v-model="state.confirmPassword"
          class="w-full"
          type="password"
          placeholder="Повторите новый пароль"
          :disabled="loading"
        />
      </UFormField>

      <UButton
        type="submit"
        color="primary"
        :loading="loading"
        :disabled="!v.safeParse(schema, state).success"
      >
        Обновить пароль
      </UButton>
    </UForm>
  </UCard>
</template>

<script setup lang="ts">
import * as v from 'valibot'
import type { FormSubmitEvent } from '@nuxt/ui'

const auth = useAuthStore()
const toast = useAppToast()
const loading = ref(false)

const schema = v.pipe(
  v.object({
    currentPassword: v.pipe(v.string(), v.minLength(1, 'Введите текущий пароль')),
    newPassword: v.pipe(v.string(), v.minLength(8, 'Пароль должен содержать минимум 8 символов')),
    confirmPassword: v.pipe(v.string(), v.minLength(8, 'Подтвердите новый пароль')),
  }),
  v.forward(
    v.partialCheck(
      [['newPassword'], ['confirmPassword']],
      (input) => input.newPassword === input.confirmPassword,
      'Пароли не совпадают',
    ),
    ['confirmPassword'],
  ),
)

type Schema = v.InferOutput<typeof schema>

const state = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

async function onSubmit(event: FormSubmitEvent<Schema>) {
  loading.value = true
  try {
    await auth.changePassword({
      current_password: event.data.currentPassword,
      new_password: event.data.newPassword,
    })
    state.currentPassword = ''
    state.newPassword = ''
    state.confirmPassword = ''
    toast.add({
      title: 'Пароль обновлен',
      description: 'Используйте новый пароль при следующем входе.',
      color: 'success',
    })
  } catch (err) {
    console.error(err)
    toast.add({
      title: 'Ошибка',
      description: err instanceof Error ? err.message : 'Не удалось сменить пароль',
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}
</script>
