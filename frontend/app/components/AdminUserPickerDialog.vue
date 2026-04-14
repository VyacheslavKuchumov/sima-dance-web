<template>
  <UModal :open="open" title="Выбор пользователя" @update:open="onOpenChange">
    <template #body>
      <div class="space-y-4">
        <div class="flex w-full flex-col gap-2 sm:flex-row">
          <UInput
            v-model="search"
            class="w-full sm:min-w-80"
            placeholder="Поиск по логину, email, ФИО или группе"
            @keyup.enter="loadUsers"
          />

          <UButton
            color="primary"
            :loading="loading"
            @click="loadUsers"
          >
            Найти
          </UButton>
        </div>

        <UProgress v-if="loading" animation="swing" />

        <template v-else>
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

          <div v-else class="max-h-[60vh] space-y-4 overflow-y-auto pr-1">
            <article
              v-for="user in users"
              :key="user.id"
              class="rounded-2xl border p-4"
              :class="isSelected(user) ? 'border-primary bg-primary/5' : 'border-default'"
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
                    <UBadge v-if="isSelected(user)" color="primary" variant="subtle">Выбран</UBadge>
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
                    color="primary"
                    :variant="isSelected(user) ? 'soft' : 'solid'"
                    @click="selectUser(user)"
                  >
                    {{ isSelected(user) ? 'Оставить выбранным' : 'Выбрать пользователя' }}
                  </UButton>
                </div>
              </div>
            </article>
          </div>
        </template>
      </div>
    </template>

    <template #footer>
      <UButton color="neutral" variant="outline" @click="onOpenChange(false)">
        Закрыть
      </UButton>
    </template>
  </UModal>
</template>

<script setup>
const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  selectedUserId: {
    type: [String, Number],
    default: '',
  },
})

const emit = defineEmits(['update:open', 'select'])

const { request } = useAdminApi()
const toast = useAppToast()

const loading = ref(false)
const search = ref('')
const users = ref([])
const registeredUsersCount = ref(0)

function onOpenChange(value) {
  emit('update:open', value)
}

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

function isSelected(user) {
  return String(user.id) === String(props.selectedUserId ?? '')
}

function selectUser(user) {
  emit('select', user)
  onOpenChange(false)
}

async function loadUsers() {
  loading.value = true

  try {
    const response = await request('/api/backend/accounts/admin/users/', {
      query: search.value.trim()
        ? { search: search.value.trim() }
        : {},
    })
    const normalizedUsers = Array.isArray(response) ? response : []
    users.value = normalizedUsers

    if (!search.value.trim()) {
      registeredUsersCount.value = normalizedUsers.length
    }
  } catch (error) {
    console.error('Failed to load users for picker', error)
    toast.add({
      title: 'Не удалось загрузить пользователей',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) return
    void loadUsers()
  },
)
</script>
