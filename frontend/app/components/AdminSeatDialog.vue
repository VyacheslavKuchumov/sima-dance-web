<template>
  <UModal :open="open" :title="modalTitle" @update:open="onOpenChange">
    <template #body>
      <div v-if="loading" class="space-y-4">
        <UProgress animation="swing" />
      </div>

      <div v-else-if="detail" class="space-y-6">
        <UAlert
          color="info"
          variant="subtle"
          title="Режим администратора"
          description="Из этого окна можно назначать и удалять брони пользователей. Само место отсюда удалить нельзя."
        />

        <div class="grid gap-4 lg:grid-cols-2">
          <section class="rounded-2xl border border-default p-4">
            <h3 class="text-base font-semibold">Информация о месте</h3>

            <div class="mt-3 space-y-2 text-sm text-toned">
              <p><span class="font-semibold">Секция:</span> {{ detail.seat.section }}</p>
              <p><span class="font-semibold">Ряд:</span> {{ detail.seat.row }}</p>
              <p><span class="font-semibold">Место:</span> {{ detail.seat.number }}</p>
              <p><span class="font-semibold">Цена:</span> {{ formatPrice(detail.seat.price) }}</p>
              <p><span class="font-semibold">Доступность:</span> {{ detail.seat.available ? 'Доступно' : 'Отключено' }}</p>
              <p><span class="font-semibold">Событие:</span> {{ detail.event.title }}</p>
            </div>
          </section>

          <section class="rounded-2xl border border-default p-4">
            <div class="flex items-center justify-between gap-3">
              <h3 class="text-base font-semibold">Текущая бронь</h3>
              <UBadge
                v-if="currentBooking"
                :color="currentBooking.status === 'booked' ? 'success' : 'warning'"
                variant="subtle"
              >
                {{ currentBooking.status === 'booked' ? 'Подтверждено' : 'Удержание' }}
              </UBadge>
            </div>

            <div v-if="currentBooking" class="mt-3 space-y-2 text-sm text-toned">
              <p><span class="font-semibold">Пользователь:</span> {{ userLabel(currentBooking) }}</p>
              <p><span class="font-semibold">ФИО:</span> {{ currentBooking.user_details?.profile?.full_name || '—' }}</p>
              <p><span class="font-semibold">ФИО ребенка:</span> {{ currentBooking.user_details?.profile?.child_full_name || '—' }}</p>
              <p><span class="font-semibold">Создано:</span> {{ formatDateTime(currentBooking.created_at) }}</p>
              <p><span class="font-semibold">Действует до:</span> {{ formatDateTime(currentBooking.expires_at) }}</p>
            </div>

            <UAlert
              v-else
              class="mt-3"
              color="neutral"
              variant="subtle"
              title="Место свободно"
              description="Сейчас у этого места нет активной брони."
            />
          </section>
        </div>

        <section class="rounded-2xl border border-default p-4">
          <div class="space-y-1">
            <h3 class="text-base font-semibold">Назначить бронь пользователю</h3>
            <p class="text-sm text-muted">
              Назначение доступно только для свободного места без активной брони.
            </p>
          </div>

          <UAlert
            v-if="currentBooking"
            class="mt-4"
            color="warning"
            variant="subtle"
            title="Сначала освободите место"
            description="Пока у места есть активная бронь, назначение нового пользователя недоступно."
          />

          <template v-else>
            <div class="mt-4 grid gap-3 lg:grid-cols-[minmax(0,2fr)_220px_180px]">
              <UInput
                v-model="userSearch"
                class="w-full"
                placeholder="Фильтр по пользователям"
              />

              <select
                v-model="selectedUserId"
                class="w-full"
              >
                <option value="" disabled>Выберите пользователя</option>
                <option v-for="user in visibleUsers" :key="user.id" :value="String(user.id)">
                  {{ userOptionLabel(user) }}
                </option>
              </select>

              <select
                v-model="selectedStatus"
                class="w-full"
              >
                <option value="booked">Подтвержденная бронь</option>
                <option value="held">Удержание</option>
              </select>
            </div>

            <div v-if="selectedStatus === 'held'" class="mt-3 max-w-xs">
              <UFormField label="Держать место, минут">
                <UInput
                  v-model="holdMinutes"
                  class="w-full"
                  type="number"
                  min="1"
                  max="1440"
                />
              </UFormField>
            </div>
          </template>
        </section>
      </div>
    </template>

    <template #footer>
      <UButton
        v-if="currentBooking"
        color="error"
        :loading="deleting"
        @click="openDeleteConfirmation"
      >
        Удалить бронь
      </UButton>

      <UButton
        v-else
        color="primary"
        :loading="saving"
        :disabled="!selectedUserId"
        @click="assignBooking"
      >
        Назначить бронь
      </UButton>
    </template>
  </UModal>

  <UModal v-model:open="deleteConfirmationOpen" title="Удалить бронь?">
    <template #body>
      <div class="space-y-3">
        <p class="text-sm text-toned">
          После удаления место снова станет свободным, и на него можно будет назначить новую бронь.
        </p>

        <div
          v-if="bookingPendingDeletion"
          class="rounded-xl border border-red-200 bg-red-50/60 p-4 text-sm text-red-900 dark:border-red-800 dark:bg-red-950/30 dark:text-red-100"
        >
          <p><span class="font-semibold">Событие:</span> {{ detail?.event?.title || '—' }}</p>
          <p><span class="font-semibold">Место:</span> {{ detail?.seat?.section }}, ряд {{ detail?.seat?.row }}, место {{ detail?.seat?.number }}</p>
          <p><span class="font-semibold">Пользователь:</span> {{ userLabel(bookingPendingDeletion) }}</p>
        </div>
      </div>
    </template>

    <template #footer>
      <UButton
        color="neutral"
        variant="outline"
        :disabled="deleting"
        @click="closeDeleteConfirmation"
      >
        Отмена
      </UButton>

      <UButton
        color="error"
        :loading="deleting"
        @click="deleteCurrentBooking"
      >
        Удалить бронь
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
  eventId: {
    type: [String, Number],
    required: true,
  },
  seat: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['changed', 'update:open'])

const { request } = useAdminApi()
const toast = useAppToast()

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const detail = ref(null)
const users = ref([])
const userSearch = ref('')
const selectedUserId = ref('')
const selectedStatus = ref('booked')
const holdMinutes = ref('30')
const deleteConfirmationOpen = ref(false)
const bookingPendingDeletion = ref(null)

const modalTitle = computed(() => {
  if (!props.seat) return 'Управление местом'
  return `Место ${props.seat.section}, ряд ${props.seat.row}, №${props.seat.number}`
})

const currentBooking = computed(() => detail.value?.current_booking ?? null)
const visibleUsers = computed(() => {
  const query = userSearch.value.trim().toLowerCase()

  if (!query) return users.value

  return users.value.filter((user) => {
    const haystack = [
      user.username,
      user.email,
      user.profile?.full_name,
      user.profile?.child_full_name,
      user.profile?.group?.name,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    return haystack.includes(query)
  })
})

function onOpenChange(value) {
  emit('update:open', value)
}

function openDeleteConfirmation() {
  if (!currentBooking.value) return
  bookingPendingDeletion.value = currentBooking.value
  deleteConfirmationOpen.value = true
}

function closeDeleteConfirmation() {
  deleteConfirmationOpen.value = false
  bookingPendingDeletion.value = null
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

function formatPrice(value) {
  const amount = Number.parseFloat(value ?? 0)
  return `${new Intl.NumberFormat('ru-RU').format(Number.isFinite(amount) ? amount : 0)} ₽`
}

function userLabel(booking) {
  const fullName = booking?.user_details?.profile?.full_name
  if (fullName) {
    return `${fullName} (${booking.user_details.username})`
  }

  return booking?.user_details?.username || booking?.user || `Пользователь #${booking?.user_id ?? '—'}`
}

function userOptionLabel(user) {
  const parts = [user.username]

  if (user.profile?.full_name) {
    parts.push(user.profile.full_name)
  }

  if (user.profile?.group?.name) {
    parts.push(user.profile.group.name)
  }

  return parts.join(' • ')
}

function syncFormFromDetail() {
  if (currentBooking.value) {
    selectedUserId.value = String(currentBooking.value.user_id ?? '')
    selectedStatus.value = currentBooking.value.status ?? 'booked'
  } else {
    if (selectedStatus.value !== 'held' && selectedStatus.value !== 'booked') {
      selectedStatus.value = 'booked'
    }
  }

  if (!currentBooking.value && !selectedUserId.value) {
    selectedUserId.value = ''
  }
}

async function loadUsers() {
  if (users.value.length) return

  const response = await request('/api/backend/accounts/admin/users/')
  users.value = Array.isArray(response) ? response : []
}

async function loadDetail() {
  if (!props.seat?.id) return

  detail.value = await request(`/api/backend/booking/events/${props.eventId}/seats/${props.seat.id}/admin/`)
}

async function loadDialog() {
  if (!props.open || !props.seat?.id) return

  loading.value = true

  try {
    await Promise.all([loadUsers(), loadDetail()])
    syncFormFromDetail()
  } catch (error) {
    console.error('Failed to load admin seat dialog', error)
    toast.add({
      title: 'Не удалось загрузить место',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}

async function assignBooking() {
  if (!selectedUserId.value || !props.seat?.id || currentBooking.value) return

  saving.value = true

  try {
    await request(`/api/backend/booking/events/${props.eventId}/seats/${props.seat.id}/admin/`, {
      method: 'POST',
      body: {
        user_id: Number(selectedUserId.value),
        status: selectedStatus.value,
        ...(selectedStatus.value === 'held'
          ? { hold_minutes: Number.parseInt(holdMinutes.value || '30', 10) || 30 }
          : {}),
      },
    })

    await loadDetail()
    syncFormFromDetail()
    emit('changed')
    toast.add({
      title: 'Бронь назначена',
      description: 'Место закреплено за выбранным пользователем.',
      color: 'success',
    })
  } catch (error) {
    console.error('Failed to assign admin booking', error)
    toast.add({
      title: 'Не удалось назначить бронь',
      description: error?.message ?? 'Проверьте выбранного пользователя и повторите попытку.',
      color: 'error',
    })
  } finally {
    saving.value = false
  }
}

async function deleteCurrentBooking() {
  if (!bookingPendingDeletion.value?.id) return

  deleting.value = true

  try {
    await request(`/api/backend/booking/bookings/${bookingPendingDeletion.value.id}/release/`, {
      method: 'POST',
    })

    await loadDetail()
    syncFormFromDetail()
    closeDeleteConfirmation()
    emit('changed')
    toast.add({
      title: 'Бронь удалена',
      description: 'Место освобождено.',
      color: 'success',
    })
  } catch (error) {
    console.error('Failed to delete admin booking', error)
    toast.add({
      title: 'Не удалось удалить бронь',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    deleting.value = false
  }
}

watch(
  () => [props.open, props.eventId, props.seat?.id],
  ([isOpen]) => {
    if (!isOpen) return
    void loadDialog()
  },
  { immediate: true },
)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) return
    closeDeleteConfirmation()
  },
)
</script>
