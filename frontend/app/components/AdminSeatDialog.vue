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
              <p><span class="font-semibold">Удержание:</span> {{ formatHoldState(currentBooking) }}</p>
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
            <div class="mt-4 space-y-4">
              <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div class="space-y-1">
                  <p class="text-sm font-medium text-toned">
                    Пользователь для назначения
                  </p>
                  <p class="text-sm text-muted">
                    Откройте поиск и выберите пользователя из отдельного окна.
                  </p>
                </div>

                <UButton
                  color="primary"
                  variant="soft"
                  icon="i-lucide-search"
                  @click="userPickerOpen = true"
                >
                  {{ selectedUser ? 'Сменить пользователя' : 'Выбрать пользователя' }}
                </UButton>
              </div>

              <UAlert
                v-if="!selectedUser"
                color="neutral"
                variant="subtle"
                title="Пользователь пока не выбран"
                description="Откройте окно поиска пользователей, чтобы назначить бронь."
              />

              <article
                v-else
                class="rounded-2xl border border-primary/20 bg-primary/5 p-4"
              >
                <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div class="space-y-2">
                    <div class="flex flex-wrap items-center gap-2">
                      <h4 class="text-lg font-semibold">{{ selectedUser.username }}</h4>
                      <UBadge v-if="selectedUser.is_superuser" color="error" variant="subtle">SUPERUSER</UBadge>
                      <UBadge v-else-if="selectedUser.is_staff" color="warning" variant="subtle">STAFF</UBadge>
                      <UBadge :color="selectedUser.is_active ? 'success' : 'neutral'" variant="subtle">
                        {{ selectedUser.is_active ? 'Активен' : 'Выключен' }}
                      </UBadge>
                    </div>

                    <div class="grid gap-2 text-sm text-toned md:grid-cols-2">
                      <p><span class="font-semibold">Email:</span> {{ selectedUser.email || '—' }}</p>
                      <p><span class="font-semibold">Группа:</span> {{ selectedUser.profile?.group?.name || '—' }}</p>
                      <p><span class="font-semibold">ФИО:</span> {{ selectedUser.profile?.full_name || '—' }}</p>
                      <p><span class="font-semibold">ФИО ребенка:</span> {{ selectedUser.profile?.child_full_name || '—' }}</p>
                      <p><span class="font-semibold">Дата регистрации:</span> {{ formatDateTime(selectedUser.date_joined) }}</p>
                      <p><span class="font-semibold">Последний вход:</span> {{ formatDateTime(selectedUser.last_login) }}</p>
                    </div>
                  </div>

                  <div class="rounded-xl bg-elevated px-4 py-3 text-sm text-toned">
                    <span class="font-semibold">Броней в системе:</span> {{ selectedUser.bookings_count ?? 0 }}
                  </div>
                </div>
              </article>

              <div class="grid gap-3 lg:grid-cols-[220px]">
                <div>
                  <p class="mb-2 text-sm font-medium text-toned">Статус брони</p>
                  <select
                    v-model="selectedStatus"
                    class="w-full"
                  >
                    <option value="booked">Подтвержденная бронь</option>
                    <option value="held">Удержание</option>
                  </select>
                </div>
              </div>
            </div>
          </template>
        </section>
      </div>
    </template>

    <template #footer>
      <UButton
        v-if="currentBooking?.status === 'held'"
        color="primary"
        :loading="confirming"
        :disabled="deleting"
        @click="confirmCurrentBooking"
      >
        Подтвердить бронь
      </UButton>

      <UButton
        v-if="currentBooking"
        color="error"
        :loading="deleting"
        :disabled="confirming"
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

  <AdminUserPickerDialog
    v-model:open="userPickerOpen"
    :selected-user-id="selectedUserId"
    @select="handleUserSelected"
  />
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
const confirming = ref(false)
const detail = ref(null)
const selectedUser = ref(null)
const selectedUserId = ref('')
const selectedStatus = ref('booked')
const deleteConfirmationOpen = ref(false)
const bookingPendingDeletion = ref(null)
const userPickerOpen = ref(false)

const modalTitle = computed(() => {
  if (!props.seat) return 'Управление местом'
  return `Место ${props.seat.section}, ряд ${props.seat.row}, №${props.seat.number}`
})

const currentBooking = computed(() => detail.value?.current_booking ?? null)

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

function formatHoldState(booking) {
  if (booking?.status !== 'held') return '—'
  if (!booking?.expires_at) return 'Без ограничения'
  return formatDateTime(booking.expires_at)
}

function userLabel(booking) {
  const fullName = booking?.user_details?.profile?.full_name
  if (fullName) {
    return `${fullName} (${booking.user_details.username})`
  }

  return booking?.user_details?.username || booking?.user || `Пользователь #${booking?.user_id ?? '—'}`
}

function buildSelectedUserFromBooking(booking) {
  if (!booking?.user_details) return null

  return {
    id: booking.user_id ?? booking.user_details.id,
    username: booking.user_details.username,
    email: booking.user_details.email,
    is_superuser: booking.user_details.is_superuser,
    is_staff: booking.user_details.is_staff,
    is_active: booking.user_details.is_active,
    date_joined: booking.user_details.date_joined,
    last_login: booking.user_details.last_login,
    bookings_count: booking.user_details.bookings_count,
    profile: booking.user_details.profile,
  }
}

function handleUserSelected(user) {
  selectedUser.value = user
  selectedUserId.value = String(user?.id ?? '')
}

function syncFormFromDetail() {
  if (currentBooking.value) {
    selectedUserId.value = String(currentBooking.value.user_id ?? '')
    selectedUser.value = buildSelectedUserFromBooking(currentBooking.value)
    selectedStatus.value = currentBooking.value.status ?? 'booked'
  } else {
    selectedUserId.value = ''
    selectedUser.value = null
    if (selectedStatus.value !== 'held' && selectedStatus.value !== 'booked') {
      selectedStatus.value = 'booked'
    }
  }
}

async function loadDetail() {
  if (!props.seat?.id) return

  detail.value = await request(`/api/backend/booking/events/${props.eventId}/seats/${props.seat.id}/admin/`)
}

async function loadDialog() {
  if (!props.open || !props.seat?.id) return

  loading.value = true

  try {
    await loadDetail()
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

async function confirmCurrentBooking() {
  if (!currentBooking.value?.id || currentBooking.value.status !== 'held') return

  confirming.value = true

  try {
    await request(`/api/backend/booking/bookings/${currentBooking.value.id}/confirm/admin/`, {
      method: 'POST',
    })

    await loadDetail()
    syncFormFromDetail()
    emit('changed')
    toast.add({
      title: 'Бронь подтверждена',
      description: 'Место закреплено за пользователем.',
      color: 'success',
    })
  } catch (error) {
    console.error('Failed to confirm admin booking', error)
    toast.add({
      title: 'Не удалось подтвердить бронь',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    confirming.value = false
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
    userPickerOpen.value = false
  },
)
</script>
