<template>
  <UCard class="w-full">
    <template #header>
      <div class="space-y-1">
        <h2 class="text-xl font-semibold">Профиль</h2>
        <p class="text-sm text-muted">
          Обновите основные данные аккаунта. Изменения сохраняются сразу в ваш профиль.
        </p>
      </div>
    </template>

    <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
      <UFormField label="Логин" name="username" required>
        <UInput
          v-model="state.username"
          class="w-full"
          placeholder="Ваш логин"
          :disabled="loading"
        />
      </UFormField>

      <UFormField label="Email" name="email">
        <UInput
          v-model="state.email"
          class="w-full"
          type="email"
          placeholder="you@example.com"
          :disabled="loading"
        />
      </UFormField>

      <div class="grid gap-4 md:grid-cols-2">
        <UFormField label="Имя" name="first_name">
          <UInput
            v-model="state.first_name"
            class="w-full"
            placeholder="Имя"
            :disabled="loading"
          />
        </UFormField>

        <UFormField label="Фамилия" name="last_name">
          <UInput
            v-model="state.last_name"
            class="w-full"
            placeholder="Фамилия"
            :disabled="loading"
          />
        </UFormField>
      </div>

      <UButton
        type="submit"
        color="primary"
        :loading="loading"
        :disabled="!v.safeParse(schema, state).success"
      >
        Сохранить изменения
      </UButton>
    </UForm>
  </UCard>
</template>

<script setup lang="ts">
import * as v from 'valibot'
import type { FormSubmitEvent } from '@nuxt/ui'

const auth = useAuthStore()
const toast = useToast()
const loading = ref(false)

const schema = v.object({
  username: v.pipe(v.string(), v.minLength(2, 'Логин должен содержать минимум 2 символа')),
  email: v.union([
    v.literal(''),
    v.pipe(v.string(), v.email('Укажите корректный email')),
  ]),
  first_name: v.optional(v.string()),
  last_name: v.optional(v.string()),
})

type Schema = v.InferOutput<typeof schema>

const state = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
})

watch(
  () => auth.user,
  (user) => {
    state.username = user?.username ?? ''
    state.email = user?.email ?? ''
    state.first_name = user?.first_name ?? ''
    state.last_name = user?.last_name ?? ''
  },
  { immediate: true },
)

async function onSubmit(event: FormSubmitEvent<Schema>) {
  loading.value = true
  try {
    await auth.updateProfile({
      username: event.data.username,
      email: event.data.email || '',
      first_name: event.data.first_name || '',
      last_name: event.data.last_name || '',
    })
    toast.add({
      title: 'Профиль обновлен',
      description: 'Новые данные сохранены.',
      color: 'success',
    })
  } catch (err) {
    console.error(err)
    toast.add({
      title: 'Ошибка',
      description: err instanceof Error ? err.message : 'Не удалось обновить профиль',
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}
</script>
