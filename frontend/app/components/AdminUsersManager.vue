<template>
  <UCard class="w-full">
    <template #header>
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-1">
          <h1 class="text-2xl font-semibold">Управление пользователями</h1>
          <p class="text-sm text-muted">
            Список всех пользователей системы, включая группы, профили и количество броней.
          </p>
        </div>

        <div class="flex w-full flex-col gap-2 sm:flex-row lg:w-auto">
          <UInput
            v-model="search"
            class="w-full sm:min-w-80"
            placeholder="Поиск по логину, email, ФИО или группе"
            @keyup.enter="loadUsers"
          />

          <UButton
            color="primary"
            icon="i-lucide-user-plus"
            @click="openCreateUserModal"
          >
            Новый пользователь
          </UButton>

          <UButton
            color="neutral"
            variant="outline"
            :loading="loading"
            @click="loadUsers"
          >
            Найти
          </UButton>
        </div>
      </div>
    </template>

    <UProgress v-if="loading" animation="swing" />

    <div v-else class="space-y-4">
      <div class="grid gap-3 md:grid-cols-2">
        <div class="rounded-2xl bg-elevated px-4 py-4">
          <p class="text-xs uppercase tracking-wide text-muted">Зарегистрировано пользователей</p>
          <p class="mt-2 text-3xl font-semibold">{{ registeredUsersCount }}</p>
        </div>

        <div class="rounded-2xl bg-elevated px-4 py-4">
          <p class="text-xs uppercase tracking-wide text-muted">Показано в списке</p>
          <p class="mt-2 text-3xl font-semibold">{{ users.length }}</p>
        </div>
      </div>

      <UAlert
        v-if="!users.length"
        color="neutral"
        variant="subtle"
        title="Пользователи не найдены"
        description="Попробуйте изменить строку поиска или обновить список."
      />

      <article
        v-for="user in users"
        :key="user.id"
        class="rounded-2xl border border-default p-4"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="space-y-2">
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="text-lg font-semibold">{{ user.username }}</h2>
              <UBadge v-if="user.is_superuser" color="error" variant="subtle">SUPERUSER</UBadge>
              <UBadge v-else-if="user.is_staff" color="warning" variant="subtle">STAFF</UBadge>
              <UBadge :color="user.is_active ? 'success' : 'neutral'" variant="subtle">
                {{ user.is_active ? 'Активен' : 'Выключен' }}
              </UBadge>
            </div>

            <div class="grid gap-2 text-sm text-toned md:grid-cols-2">
              <p><span class="font-semibold">Email:</span> {{ user.email || '—' }}</p>
              <p><span class="font-semibold">Группа:</span> {{ user.profile?.group?.name || '—' }}</p>
              <p><span class="font-semibold">ФИО:</span> {{ user.profile?.full_name || '—' }}</p>
              <p><span class="font-semibold">ФИО ребенка:</span> {{ user.profile?.child_full_name || '—' }}</p>
              <p><span class="font-semibold">Дата регистрации:</span> {{ formatDateTime(user.date_joined) }}</p>
              <p><span class="font-semibold">Последний вход:</span> {{ formatDateTime(user.last_login) }}</p>
            </div>
          </div>

          <div class="flex flex-col gap-2 lg:items-end">
            <div class="rounded-xl bg-elevated px-4 py-3 text-sm text-toned">
              <span class="font-semibold">Броней в системе:</span> {{ user.bookings_count ?? 0 }}
            </div>

            <UButton
              color="warning"
              variant="soft"
              :loading="impersonatingUserId === user.id"
              :disabled="user.id === auth.userId || !user.is_active"
              @click="impersonate(user)"
            >
              {{ user.id === auth.userId ? 'Текущая сессия' : 'Войти как пользователь' }}
            </UButton>

            <UButton
              color="error"
              variant="soft"
              :loading="resettingPasswordUserId === user.id"
              @click="openResetPasswordConfirmation(user)"
            >
              Сбросить пароль
            </UButton>

            <UButton
              color="neutral"
              variant="outline"
              :to="{
                path: '/admin/bookings',
                query: {
                  userId: String(user.id),
                },
              }"
            >
              Открыть брони пользователя
            </UButton>
          </div>
        </div>
      </article>
    </div>
  </UCard>

  <UModal v-model:open="createUserModalOpen" title="Новый пользователь">
    <template #body>
      <UForm
        id="admin-create-user-form"
        :schema="createUserSchema"
        :state="createUserForm"
        class="space-y-4"
        @submit="createUser"
      >
        <UFormField label="Группа" name="groupId" required>
          <select
            v-model="createUserForm.groupId"
            name="groupId"
            class="w-full rounded-md border bg-default px-3 py-2 text-sm outline-none transition-colors disabled:cursor-not-allowed disabled:opacity-75"
            :class="createUserForm.groupId ? 'border-default focus:border-primary focus:ring-2 focus:ring-primary/20' : 'border-error focus:border-error focus:ring-2 focus:ring-error/30'"
            :aria-invalid="!createUserForm.groupId"
            :disabled="creatingUser || groupsLoading || !signupGroups.length"
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
            v-model="createUserForm.username"
            class="w-full"
            placeholder="ivanov123"
            :disabled="creatingUser"
          />
        </UFormField>

        <UFormField label="Ваше ФИО" name="full_name" required>
          <UInput
            v-model="createUserForm.full_name"
            class="w-full"
            placeholder="Иванов Иван Иванович"
            :disabled="creatingUser"
          />
        </UFormField>

        <UFormField label="ФИО ребенка" name="child_full_name" required>
          <UInput
            v-model="createUserForm.child_full_name"
            class="w-full"
            placeholder="Иванов Петр Иванович"
            :disabled="creatingUser"
          />
        </UFormField>

        <UFormField label="Пароль" name="password" required>
          <UInput
            v-model="createUserForm.password"
            class="w-full"
            type="password"
            placeholder="Придумайте пароль"
            :disabled="creatingUser"
          />
        </UFormField>

        <UFormField label="Подтверждение пароля" name="confirmPassword" required>
          <UInput
            v-model="createUserForm.confirmPassword"
            class="w-full"
            type="password"
            placeholder="Подтвердите пароль"
            :disabled="creatingUser"
          />
        </UFormField>
      </UForm>
    </template>

    <template #footer>
      <UButton
        color="neutral"
        variant="outline"
        :disabled="creatingUser"
        @click="closeCreateUserModal"
      >
        Отмена
      </UButton>

      <UButton
        type="submit"
        form="admin-create-user-form"
        color="primary"
        :loading="creatingUser"
        :disabled="!createUserFormIsValid || !signupGroups.length"
      >
        Создать пользователя
      </UButton>
    </template>
  </UModal>

  <UModal v-model:open="resetPasswordConfirmationOpen" title="Сбросить пароль?">
    <template #body>
      <div class="space-y-3">
        <p class="text-sm text-toned">
          Новый пароль будет создан автоматически. Старый пароль пользователя сразу перестанет работать.
        </p>

        <div
          v-if="userPendingPasswordReset"
          class="rounded-xl border border-red-200 bg-red-50/60 p-4 text-sm text-red-900 dark:border-red-800 dark:bg-red-950/30 dark:text-red-100"
        >
          <p><span class="font-semibold">Пользователь:</span> {{ userPendingPasswordReset.username }}</p>
          <p><span class="font-semibold">Email:</span> {{ userPendingPasswordReset.email || '—' }}</p>
          <p><span class="font-semibold">ФИО:</span> {{ userPendingPasswordReset.profile?.full_name || '—' }}</p>
        </div>
      </div>
    </template>

    <template #footer>
      <UButton
        color="neutral"
        variant="outline"
        :disabled="Boolean(resettingPasswordUserId)"
        @click="closeResetPasswordConfirmation"
      >
        Отмена
      </UButton>

      <UButton
        color="error"
        :loading="Boolean(resettingPasswordUserId)"
        @click="confirmResetPassword"
      >
        Сбросить пароль
      </UButton>
    </template>
  </UModal>

  <UModal v-model:open="resetPasswordResultOpen" title="Новый пароль">
    <template #body>
      <div class="space-y-4">
        <UAlert
          color="success"
          variant="subtle"
          title="Пароль обновлён"
          description="Покажите пользователю новый пароль. Он сгенерирован автоматически и больше не будет показан в этом действии."
        />

        <div
          v-if="resetPasswordResult"
          class="space-y-3 rounded-xl border border-default bg-elevated p-4"
        >
          <p class="text-sm text-toned">
            <span class="font-semibold">Пользователь:</span> {{ resetPasswordResult.user?.username || '—' }}
          </p>
          <div>
            <p class="mb-2 text-xs uppercase tracking-wide text-muted">Новый пароль</p>
            <div class="rounded-lg border border-default bg-default px-4 py-3 font-mono text-lg">
              {{ resetPasswordResult.generated_password }}
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <UButton color="primary" @click="closeResetPasswordResult">
        Закрыть
      </UButton>
    </template>
  </UModal>
</template>

<script setup>
import * as v from 'valibot'

const auth = useAuthStore()
const router = useRouter()
const { request } = useAdminApi()
const toast = useAppToast()

const loading = ref(false)
const groupsLoading = ref(false)
const creatingUser = ref(false)
const createUserModalOpen = ref(false)
const search = ref('')
const users = ref([])
const registeredUsersCount = ref(0)
const impersonatingUserId = ref(null)
const resettingPasswordUserId = ref(null)
const resetPasswordConfirmationOpen = ref(false)
const resetPasswordResultOpen = ref(false)
const userPendingPasswordReset = ref(null)
const resetPasswordResult = ref(null)
const signupGroups = computed(() => auth.signupGroups)

const createUserSchema = v.pipe(
  v.object({
    groupId: v.pipe(v.string(), v.minLength(1, 'Выберите группу')),
    username: v.pipe(v.string(), v.minLength(2, 'Логин должен содержать минимум 2 символа')),
    full_name: v.pipe(v.string(), v.minLength(2, 'Укажите ФИО')),
    child_full_name: v.pipe(v.string(), v.minLength(2, 'Укажите ФИО ребенка')),
    password: v.pipe(v.string(), v.minLength(8, 'Пароль должен содержать минимум 8 символов')),
    confirmPassword: v.string(),
  }),
  v.forward(
    v.partialCheck(
      [['password'], ['confirmPassword']],
      (input) => input.password === input.confirmPassword,
      'Пароли не совпадают',
    ),
    ['confirmPassword'],
  ),
)

const createUserForm = reactive({
  groupId: '',
  username: '',
  full_name: '',
  child_full_name: '',
  password: '',
  confirmPassword: '',
})

const createUserFormIsValid = computed(() => v.safeParse(createUserSchema, createUserForm).success)

function formatDateTime(value) {
  if (!value) return '—'

  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function resetCreateUserForm() {
  createUserForm.groupId = ''
  createUserForm.username = ''
  createUserForm.full_name = ''
  createUserForm.child_full_name = ''
  createUserForm.password = ''
  createUserForm.confirmPassword = ''
}

async function loadSignupGroups() {
  groupsLoading.value = true

  try {
    await auth.fetchSignupGroups()
  } catch (error) {
    console.error('Failed to load signup groups for admin users', error)
    toast.add({
      title: 'Не удалось загрузить группы',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    groupsLoading.value = false
  }
}

function openCreateUserModal() {
  resetCreateUserForm()
  createUserModalOpen.value = true
  if (!signupGroups.value.length) {
    void loadSignupGroups()
  }
}

function closeCreateUserModal() {
  if (creatingUser.value) return

  createUserModalOpen.value = false
  resetCreateUserForm()
}

async function loadUsers() {
  loading.value = true

  try {
    const response = await request('/api/backend/accounts/admin/users/', {
      query: search.value
        ? { search: search.value.trim() }
        : {},
    })
    const normalizedUsers = Array.isArray(response) ? response : []
    users.value = normalizedUsers

    if (!search.value.trim()) {
      registeredUsersCount.value = normalizedUsers.length
    }
  } catch (error) {
    console.error('Failed to load admin users', error)
    toast.add({
      title: 'Не удалось загрузить пользователей',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}

async function createUser(event) {
  creatingUser.value = true

  try {
    const response = await request('/api/backend/accounts/admin/users/', {
      method: 'POST',
      body: {
        username: event.data.username.trim(),
        password: event.data.password,
        group: Number(event.data.groupId),
        full_name: event.data.full_name.trim(),
        child_full_name: event.data.child_full_name.trim(),
      },
    })

    search.value = ''
    await loadUsers()
    createUserModalOpen.value = false
    resetCreateUserForm()

    toast.add({
      title: 'Пользователь создан',
      description: `Аккаунт ${response?.username ?? event.data.username} зарегистрирован.`,
      color: 'success',
    })
  } catch (error) {
    console.error('Failed to create user from admin panel', error)
    toast.add({
      title: 'Не удалось создать пользователя',
      description: error?.data?.statusMessage ?? error?.message ?? 'Проверьте данные и повторите попытку.',
      color: 'error',
    })
  } finally {
    creatingUser.value = false
  }
}

async function impersonate(user) {
  impersonatingUserId.value = user.id

  try {
    await auth.impersonateUser(user.id)
    toast.add({
      title: 'Сессия переключена',
      description: `Вы вошли как ${user.username}.`,
      color: 'warning',
    })
    await router.push('/')
  } catch (error) {
    console.error('Failed to impersonate user', error)
    toast.add({
      title: 'Не удалось войти за пользователя',
      description: error?.data?.user_id?.[0] ?? error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    impersonatingUserId.value = null
  }
}

function openResetPasswordConfirmation(user) {
  userPendingPasswordReset.value = user
  resetPasswordConfirmationOpen.value = true
}

function closeResetPasswordConfirmation() {
  resetPasswordConfirmationOpen.value = false
  userPendingPasswordReset.value = null
}

function closeResetPasswordResult() {
  resetPasswordResultOpen.value = false
  resetPasswordResult.value = null
}

async function confirmResetPassword() {
  if (!userPendingPasswordReset.value) return

  const user = userPendingPasswordReset.value
  resettingPasswordUserId.value = user.id

  try {
    const response = await request('/api/backend/accounts/admin/reset-password/', {
      method: 'POST',
      body: {
        user_id: user.id,
      },
    })

    closeResetPasswordConfirmation()
    resetPasswordResult.value = response
    resetPasswordResultOpen.value = true

    toast.add({
      title: 'Пароль сброшен',
      description: `Для ${user.username} создан новый пароль.`,
      color: 'success',
    })
  } catch (error) {
    console.error('Failed to reset user password', error)
    toast.add({
      title: 'Не удалось сбросить пароль',
      description: error?.data?.user_id?.[0] ?? error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    resettingPasswordUserId.value = null
  }
}

watch(resetPasswordConfirmationOpen, (value) => {
  if (!value && !resettingPasswordUserId.value) {
    userPendingPasswordReset.value = null
  }
})

watch(resettingPasswordUserId, (value) => {
  if (!value && !resetPasswordConfirmationOpen.value) {
    userPendingPasswordReset.value = null
  }
})

watch(resetPasswordResultOpen, (value) => {
  if (!value) {
    resetPasswordResult.value = null
  }
})

onMounted(() => {
  void loadUsers()
  void loadSignupGroups()
})
</script>
