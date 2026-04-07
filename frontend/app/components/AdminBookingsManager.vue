<template>
  <UCard class="w-full">
    <template #header>
      <div class="space-y-4">
        <div class="space-y-1">
          <h1 class="text-2xl font-semibold">Управление бронями</h1>
          <p class="text-sm text-gray-500">
            Просматривайте все активные удержания и подтвержденные места, удаляйте бронь и переходите к нужному концерту.
          </p>
        </div>

        <div class="grid gap-3 lg:grid-cols-[minmax(0,2fr)_220px_180px_180px_auto]">
          <UInput
            v-model="filters.search"
            class="w-full"
            placeholder="Поиск по пользователю, событию или секции"
            @keyup.enter="applyFilters"
          />

          <select
            v-model="filters.eventId"
            class="w-full"
          >
            <option value="">Все концерты</option>
            <option v-for="event in events" :key="event.id" :value="String(event.id)">
              {{ event.title }}
            </option>
          </select>

          <select
            v-model="filters.status"
            class="w-full"
          >
            <option value="held,booked">Все статусы</option>
            <option value="held">Только удержания</option>
            <option value="booked">Только подтвержденные</option>
          </select>

          <UInput
            v-model="filters.userId"
            class="w-full"
            placeholder="ID пользователя"
            @keyup.enter="applyFilters"
          />

          <div class="flex gap-2">
            <UButton color="primary" :loading="loading" @click="applyFilters">
              Применить
            </UButton>

            <UButton color="neutral" variant="outline" @click="resetFilters">
              Сбросить
            </UButton>
          </div>
        </div>
      </div>
    </template>

    <UProgress v-if="loading" animation="swing" />

    <div v-else class="space-y-4">
      <UAlert
        v-if="!bookings.length"
        color="neutral"
        variant="subtle"
        title="Брони не найдены"
        description="Измените фильтры или дождитесь новых бронирований."
      />

      <article
        v-for="booking in bookings"
        :key="booking.id"
        class="rounded-2xl border border-gray-200 p-4"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="space-y-2">
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="text-lg font-semibold">{{ booking.event_title || `Событие #${booking.event}` }}</h2>
              <UBadge :color="booking.status === 'booked' ? 'success' : 'warning'" variant="subtle">
                {{ booking.status === 'booked' ? 'Подтверждено' : 'Удержание' }}
              </UBadge>
            </div>

            <div class="grid gap-2 text-sm text-gray-600 md:grid-cols-2">
              <p><span class="font-medium text-gray-900">Пользователь:</span> {{ userLabel(booking) }}</p>
              <p><span class="font-medium text-gray-900">Место:</span> {{ seatLabel(booking) }}</p>
              <p><span class="font-medium text-gray-900">Создано:</span> {{ formatDateTime(booking.created_at) }}</p>
              <p><span class="font-medium text-gray-900">Действует до:</span> {{ formatDateTime(booking.expires_at) }}</p>
              <p><span class="font-medium text-gray-900">Стоимость:</span> {{ formatPrice(booking.price_snapshot) }}</p>
              <p><span class="font-medium text-gray-900">ID брони:</span> {{ booking.id }}</p>
            </div>
          </div>

          <div class="flex flex-col gap-2 sm:flex-row lg:flex-col">
            <UButton
              color="neutral"
              variant="outline"
              :to="`/seats/${booking.event}`"
            >
              Схема зала
            </UButton>

            <UButton
              color="error"
              :loading="removingBookingId === booking.id"
              @click="removeBooking(booking)"
            >
              Удалить бронь
            </UButton>
          </div>
        </div>
      </article>
    </div>
  </UCard>
</template>

<script setup>
const { request } = useAdminApi()
const toast = useAppToast()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const removingBookingId = ref(null)
const bookings = ref([])
const events = ref([])

const filters = reactive({
  search: '',
  status: 'held,booked',
  eventId: '',
  userId: '',
})

function syncFiltersFromRoute() {
  filters.search = typeof route.query.search === 'string' ? route.query.search : ''
  filters.status = typeof route.query.status === 'string' ? route.query.status : 'held,booked'
  filters.eventId = typeof route.query.eventId === 'string' ? route.query.eventId : ''
  filters.userId = typeof route.query.userId === 'string' ? route.query.userId : ''
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

async function loadEvents() {
  try {
    const response = await request('/api/backend/booking/events/')
    events.value = Array.isArray(response) ? response : response?.results ?? []
  } catch (error) {
    console.error('Failed to load events for admin bookings', error)
  }
}

async function loadBookings() {
  loading.value = true

  try {
    const response = await request('/api/backend/booking/bookings/', {
      query: {
        all_users: 'true',
        active_only: 'true',
        status: filters.status,
        ...(filters.eventId ? { event_id: filters.eventId } : {}),
        ...(filters.userId ? { user_id: filters.userId } : {}),
        ...(filters.search.trim() ? { search: filters.search.trim() } : {}),
      },
    })

    bookings.value = Array.isArray(response) ? response : response?.results ?? []
  } catch (error) {
    console.error('Failed to load admin bookings', error)
    toast.add({
      title: 'Не удалось загрузить брони',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}

async function applyFilters() {
  await router.replace({
    query: {
      ...(filters.search.trim() ? { search: filters.search.trim() } : {}),
      ...(filters.status && filters.status !== 'held,booked' ? { status: filters.status } : {}),
      ...(filters.eventId ? { eventId: filters.eventId } : {}),
      ...(filters.userId ? { userId: filters.userId } : {}),
    },
  })
}

async function resetFilters() {
  filters.search = ''
  filters.status = 'held,booked'
  filters.eventId = ''
  filters.userId = ''
  await router.replace({ query: {} })
}

async function removeBooking(booking) {
  removingBookingId.value = booking.id

  try {
    await request(`/api/backend/booking/bookings/${booking.id}/release/`, {
      method: 'POST',
    })
    toast.add({
      title: 'Бронь удалена',
      description: 'Место снова доступно в схеме зала.',
      color: 'success',
    })
    await loadBookings()
  } catch (error) {
    console.error('Failed to remove admin booking', error)
    toast.add({
      title: 'Не удалось удалить бронь',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    removingBookingId.value = null
  }
}

watch(
  () => route.query,
  () => {
    syncFiltersFromRoute()
    void loadBookings()
  },
  { immediate: true, deep: true },
)

onMounted(() => {
  syncFiltersFromRoute()
  void loadEvents()
})
</script>
