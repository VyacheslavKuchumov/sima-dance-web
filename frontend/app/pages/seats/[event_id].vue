<template>
  <div class="w-full space-y-6">
    <header class="space-y-2">
      <p class="text-sm uppercase tracking-[0.2em] text-muted">Бронирование</p>
      <h1 class="text-3xl font-semibold">
        {{ event?.title || 'Выбор мест' }}
      </h1>
      <p class="text-sm text-muted">
        {{ eventDateLabel }}
      </p>
    </header>

    <div class="layout-grid">
      <SeatsList
        :event-id="eventId"
        @admin-changed="adminRefreshKey += 1"
      />

      <div :class="auth.isSuperuser ? 'hidden lg:block' : 'block'">
        <AdminRecentBookings
          v-if="auth.isSuperuser"
          :event-id="eventId"
          :refresh-key="adminRefreshKey"
        />

        <BookingCart
          v-else
          :event-id="eventId"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const auth = useAuthStore()
const adminRefreshKey = ref(0)

const eventId = computed(() => String(route.params.event_id))

const { data } = useFetch(() => `/api/backend/booking/events/${eventId.value}/`, {
  server: false,
  default: () => null,
})

const event = computed(() => data.value)
const eventDateLabel = computed(() => {
  if (!event.value?.starts_at) {
    return 'Выберите места слева и завершите подтверждение через раздел «Мои брони».'
  }

  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(new Date(event.value.starts_at))
})
</script>

<style scoped>
.layout-grid {
  display: grid;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .layout-grid {
    grid-template-columns: minmax(0, 2fr) minmax(320px, 1fr);
    align-items: start;
  }
}
</style>
