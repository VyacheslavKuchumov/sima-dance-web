<template>
  <UCard class="w-full">
    <template #header>
      <div class="flex items-start justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold">Последние брони</h2>
          <p class="text-sm text-gray-500">
            Свежие удержания и подтверждения по текущему концерту.
          </p>
        </div>

        <UButton
          icon="i-lucide-refresh-cw"
          color="neutral"
          variant="outline"
          :loading="loading"
          @click="loadBookings"
        >
          Обновить
        </UButton>
      </div>
    </template>

    <div class="space-y-3">
      <UAlert
        v-if="!bookings.length && !loading"
        color="neutral"
        variant="subtle"
        title="Активных броней пока нет"
        description="Как только места будут удержаны или подтверждены, они появятся здесь."
      />

      <article
        v-for="booking in visibleBookings"
        :key="booking.id"
        class="rounded-2xl border border-gray-200 p-4"
      >
        <div class="space-y-2">
          <div class="flex items-center justify-between gap-3">
            <p class="font-medium">{{ seatLabel(booking) }}</p>
            <UBadge :color="booking.status === 'booked' ? 'success' : 'warning'" variant="subtle">
              {{ booking.status === 'booked' ? 'Подтверждено' : 'Удержание' }}
            </UBadge>
          </div>

          <p class="text-sm text-gray-600">{{ userLabel(booking) }}</p>
          <p class="text-sm text-gray-500">Создано: {{ formatDateTime(booking.created_at) }}</p>
        </div>
      </article>
    </div>

    <template #footer>
      <UButton
        color="primary"
        block
        :to="{
          path: '/admin/bookings',
          query: {
            eventId: String(eventId),
          },
        }"
      >
        Перейти в список броней
      </UButton>
    </template>
  </UCard>
</template>

<script setup>
const props = defineProps({
  eventId: {
    type: [String, Number],
    required: true,
  },
  refreshKey: {
    type: Number,
    default: 0,
  },
})

const { request } = useAdminApi()
const toast = useAppToast()

const loading = ref(false)
const bookings = ref([])

const visibleBookings = computed(() => bookings.value.slice(0, 8))

function formatDateTime(value) {
  if (!value) return '—'

  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function seatLabel(booking) {
  if (!booking?.seat) return '—'
  return `${booking.seat.section}, ряд ${booking.seat.row}, место ${booking.seat.number}`
}

function userLabel(booking) {
  const fullName = booking?.user_details?.profile?.full_name
  if (fullName) {
    return `${fullName} (${booking.user_details.username})`
  }

  return booking?.user_details?.username || booking?.user || `Пользователь #${booking?.user_id ?? '—'}`
}

async function loadBookings() {
  loading.value = true

  try {
    const response = await request('/api/backend/booking/bookings/', {
      query: {
        all_users: 'true',
        active_only: 'true',
        status: 'held,booked',
        event_id: String(props.eventId),
      },
    })
    bookings.value = Array.isArray(response) ? response : response?.results ?? []
  } catch (error) {
    console.error('Failed to load recent admin bookings', error)
    toast.add({
      title: 'Не удалось загрузить последние брони',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.eventId, props.refreshKey],
  () => {
    void loadBookings()
  },
  { immediate: true },
)
</script>
