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
      <UFormField label="Группа" name="groupId" required>
        <select
          id="profile-groupId"
          v-model="state.groupId"
          name="groupId"
          class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/40 disabled:cursor-not-allowed disabled:opacity-60"
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

      <UButton
        type="submit"
        color="primary"
        :loading="loading"
        :disabled="!v.safeParse(schema, state).success || !signupGroups.length"
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
const toast = useAppToast()
const loading = ref(false)
const signupGroups = computed(() => auth.signupGroups)

const schema = v.object({
  groupId: v.pipe(v.string(), v.minLength(1, 'Выберите группу')),
  username: v.pipe(v.string(), v.minLength(2, 'Логин должен содержать минимум 2 символа')),
  email: v.union([
    v.literal(''),
    v.pipe(v.string(), v.email('Укажите корректный email')),
  ]),
  full_name: v.pipe(v.string(), v.minLength(2, 'Укажите ваше ФИО')),
  child_full_name: v.pipe(v.string(), v.minLength(2, 'Укажите ФИО ребенка')),
})

type Schema = v.InferOutput<typeof schema>

const state = reactive({
  groupId: '',
  username: '',
  email: '',
  full_name: '',
  child_full_name: '',
})

watch(
  () => auth.user,
  (user) => {
    state.username = user?.username ?? ''
    state.email = user?.email ?? ''
    state.groupId = user?.profile?.group?.id ? String(user.profile.group.id) : ''
    state.full_name = user?.profile?.full_name ?? ''
    state.child_full_name = user?.profile?.child_full_name ?? ''
  },
  { immediate: true },
)

onMounted(() => {
  void auth.fetchSignupGroups().catch((error) => {
    console.error('Failed to load profile groups', error)
  })
})

async function onSubmit(event: FormSubmitEvent<Schema>) {
  loading.value = true
  try {
    await auth.updateProfile({
      group: Number(event.data.groupId),
      username: event.data.username,
      email: event.data.email || '',
      full_name: event.data.full_name,
      child_full_name: event.data.child_full_name,
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
