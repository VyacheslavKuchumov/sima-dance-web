
<template>
  <UCard class="w-full max-w-md">
    <template #header>
      <div class="space-y-1">
        <h2 class="text-xl font-semibold">Регистрация</h2>
        <p class="text-sm text-muted">
          Выберите группу и заполните данные, чтобы создать аккаунт.
        </p>
      </div>
    </template>

    <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
      <UFormField label="Группа" name="groupId" required>
        <select
          id="groupId"
          v-model="state.groupId"
          name="groupId"
          class="w-full"
          :disabled="loading || !signupGroups.length"
        >
          <option value="" disabled>
            {{ signupGroups.length ? 'Выберите группу' : 'Группы не найдены' }}
          </option>
          <option v-for="group in signupGroups" :key="group.id" :value="String(group.id)">
            {{ group.name }}
          </option>
        </select>
      </UFormField>

      <UFormField label="Логин" name="username" required>
        <UInput
          v-model="state.username"
          class="w-full"
          placeholder="Придумайте логин"
          :disabled="loading"
        />
      </UFormField>

      <UFormField label="Ваше ФИО" name="full_name" required>
        <UInput
          v-model="state.full_name"
          class="w-full"
          placeholder="Иванов Иван Иванович"
          :disabled="loading"
        />
      </UFormField>

      <UFormField label="ФИО ребенка" name="child_full_name" required>
        <UInput
          v-model="state.child_full_name"
          class="w-full"
          placeholder="Иванов Петр Иванович"
          :disabled="loading"
        />
      </UFormField>

      <UFormField label="Пароль" name="password" required>
        <UInput
          v-model="state.password"
          class="w-full"
          type="password"
          placeholder="Придумайте пароль"
          :disabled="loading"
        />
      </UFormField>

      <UFormField label="Подтверждение пароля" name="confirmPassword" required>
        <UInput
          v-model="state.confirmPassword"
          class="w-full"
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
        :disabled="!v.safeParse(schema, state).success || !signupGroups.length"
      >
        Регистрация
      </UButton>
    </UForm>

    <template #footer>
      <div class="text-center">
        Уже есть аккаунт?
        <NuxtLink to="/login" class="ml-1 text-primary underline">
          Войти в аккаунт
        </NuxtLink>
      </div>
    </template>
  </UCard>

</template>

<script setup lang="ts">

import * as v from 'valibot'
import type { FormSubmitEvent } from '@nuxt/ui'

const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()
const signupGroups = computed(() => auth.signupGroups)

const schema = v.pipe(
  v.object({
    groupId: v.pipe(
      v.string(),
      v.minLength(1, 'Выберите группу'),
    ),
    username: v.pipe(
      v.string(),
      v.minLength(2, 'Имя пользователя должно содержать минимум 2 символа')
    ),
    full_name: v.pipe(
      v.string(),
      v.minLength(2, 'Укажите ваше ФИО'),
    ),
    child_full_name: v.pipe(
      v.string(),
      v.minLength(2, 'Укажите ФИО ребенка'),
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
  groupId: '',
  username: '',
  full_name: '',
  child_full_name: '',
  password: '',
  confirmPassword: ''
})

onMounted(() => {
  void auth.fetchSignupGroups().catch((error) => {
    console.error('Failed to load signup groups', error)
  })
})

const toast = useAppToast()
async function onSubmit(event: FormSubmitEvent<Schema>) {
  loading.value = true
  try {
    await auth.signup({
      username: event.data.username,
      password: event.data.password,
      group: Number(event.data.groupId),
      full_name: event.data.full_name,
      child_full_name: event.data.child_full_name,
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
